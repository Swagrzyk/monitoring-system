# CI: co sprawdza pipeline i jak to uruchomić lokalnie

Pipeline jest w jednym pliku: [.github/workflows/ci.yml](../.github/workflows/ci.yml).
Uruchamia się przy każdym pushu na `main` i przy każdym pull requeście do `main`.
Ma pięć jobów, które działają równolegle i niezależnie od siebie.

Wszystkie sprawdzenia są statyczne: czytają pliki z repo i nic więcej.
Pipeline niczego nie wdraża i nie łączy się z żadnym klastrem.
Zielony wynik znaczy „pliki są poprawne”, a nie „system działa”.

## Warstwy sprawdzania

Każde narzędzie odpowiada na inne pytanie. Ten sam plik może przejść jedno i oblać drugie.

| Narzędzie | Pytanie | Przykład błędu, który łapie |
|---|---|---|
| yamllint | Czy to poprawny YAML? | złe wcięcie, zduplikowany klucz |
| kubeconform | Czy to poprawny obiekt Kubernetesa? | `replicas: "trzy"`, nieznane pole |
| promtool | Czy Prometheus wczyta tę konfigurację i reguły? | niedomknięty nawias w PromQL |
| hadolint | Czy Dockerfile trzyma dobre praktyki? | `USER` z nazwą zamiast numeru |
| docker build | Czy obraz w ogóle się buduje? | zła wersja pakietu w `requirements.txt` |
| terraform | Czy kod Terraform jest sformatowany i spójny? | odwołanie do zmiennej, której nie ma |

## Część wspólna workflow

- `on: push` i `on: pull_request`, oba z `branches: [main]`. Push na inną gałąź nic nie uruchamia. Pipeline rusza dopiero po otwarciu PR do `main`.
- `permissions: contents: read`. Każdy run dostaje tymczasowy token `GITHUB_TOKEN`. Tu może on tylko czytać repo. Gdyby któraś akcja została przejęta, nie zrobi tym tokenem pusha ani nie zmieni ustawień.
- Akcje są przypięte do SHA commita, np. `actions/checkout@3d3c42e...  # v7.0.1`. Tag `v7` autor akcji może przesunąć na inny kod. SHA wskazuje zawsze ten sam kod.
- `persist-credentials: false` przy checkout. Domyślnie checkout zostawia token w `.git/config`, a tu żaden krok go nie potrzebuje.
- `concurrency` z `cancel-in-progress: true`. Nowy push na tę samą gałąź anuluje poprzedni, jeszcze trwający run.
- `runs-on: ubuntu-24.04` zamiast `ubuntu-latest`, żeby system nie zmienił się sam z dnia na dzień.
- `timeout-minutes` na każdym jobie, żeby zawieszony job nie wisiał godzinami.

Krok w GitHub Actions jest nieudany wtedy, gdy polecenie kończy się kodem wyjścia innym niż 0. Nigdzie nie ma `continue-on-error`.

## Job `lint-yaml`

**Co robi.** Uruchamia `yamllint` na `k8s/`, `argocd/`, `.github/workflows/` i na samym `.yamllint`.

**Co łapie.** Błędy składni YAML, zduplikowane klucze, złe wcięcia, spacje na końcu linii.

**Czego nie łapie.** Niczego, co dotyczy Kubernetesa. Dla yamllint `replicas: "trzy"` to poprawna para klucz i napis.

**Konfiguracja** ([.yamllint](../.yamllint)):

- `line-length`: limit 120 znaków, poziom `warning`. Ostrzeżenie widać w logu, ale job przechodzi. Długie są opisy alertów i JSON dashboardu Grafany.
- `document-start: disable`: `---` na początku pliku z jednym dokumentem jest opcjonalne.
- `truthy: check-keys: false`: w YAML 1.1 słowo `on` znaczy `true`, a workflow musi mieć klucz `on:`.

**Lokalnie:**

```bash
pip install yamllint==1.38.0     # najlepiej w venv
yamllint k8s/ argocd/ .github/workflows/ .yamllint
```

Lokalnie yamllint zobaczy też `k8s/grafana/secret.yaml`. Ten plik jest w `.gitignore`, więc w CI go nie ma.

## Job `prometheus-rules`

**Problem.** Reguły i konfiguracja Prometheusa siedzą w ConfigMapach jako tekst pod kluczem `data`. `promtool` czyta zwykłe pliki, a nie ConfigMapy.

**Co robi.**

1. Skrypt [scripts/ci/extract-configmap.py](../scripts/ci/extract-configmap.py) zapisuje każdy klucz z `data` do osobnego pliku.
2. Pliki trafiają do takiego samego układu katalogów, jaki widzi pod: konfiguracja w `/etc/prometheus`, reguły w `/etc/prometheus/rules`.
3. `promtool check rules --lint-fatal` sprawdza reguły.
4. `promtool check config` sprawdza `prometheus.yml`. Dzięki układowi katalogów znajduje też pliki reguł wskazane w `rule_files`.
5. Osobny krok sprawdza stary `prometheus/prometheus.yml` (wariant systemd).

`promtool` jest uruchamiany z obrazu `prom/prometheus:v2.55.1`, czyli z tej samej wersji, która działa w klastrze. Przy zmianie wersji w `statefulset.yaml` trzeba ją zmienić też w workflow.

Układ katalogów ma znaczenie. `prometheus.yml` wskazuje reguły przez `/etc/prometheus/rules/*.yml`. Gdyby tej ścieżki nie było, `check config` uznałby, że plików reguł jest zero, i przeszedł na zielono.

**Co łapie.**

- Błąd składni PromQL, np. niedomknięty nawias: `parse error: unclosed left parenthesis`.
- Zły czas w `for:`, np. `not a valid duration string`.
- Nieznaną funkcję w szablonie opisu alertu: `function "humanizeProcent" not defined`.
- Zduplikowane reguły (`--lint-fatal` robi z tego błąd).
- Błędy w strukturze `prometheus.yml`, np. nieznane pole.

**Czego nie łapie.**

- Literówki w nazwie metryki lub etykiety. `upp{job="pyton-monitor"}` to poprawny PromQL, tylko nic nie zwraca. Alert nigdy się nie odpali i promtool tego nie zauważy.
- Złych progów. Promtool nie wie, czy `14.4 * 0.005` ma sens.
- Tego, czy cel scrape'a istnieje i odpowiada.

Na pierwsze dwa braki odpowiedzią są testy jednostkowe reguł (`promtool test rules`). Takich testów jeszcze nie ma w repo.

**Lokalnie:**

```bash
OUT=$(mktemp -d)
python3 scripts/ci/extract-configmap.py k8s/prometheus/configmap.yaml "$OUT"
python3 scripts/ci/extract-configmap.py k8s/prometheus/configmap-rules.yaml "$OUT/rules"
chmod -R a+rX "$OUT"

docker run --rm -v "$OUT:/etc/prometheus:ro" --entrypoint sh prom/prometheus:v2.55.1 \
  -c 'promtool check rules --lint-fatal /etc/prometheus/rules/*.yml'

docker run --rm -v "$OUT:/etc/prometheus:ro" --entrypoint promtool prom/prometheus:v2.55.1 \
  check config /etc/prometheus/prometheus.yml
```

Skrypt potrzebuje PyYAML (`pip install PyYAML`). `chmod` jest po to, żeby użytkownik `nobody` w kontenerze mógł czytać katalog z `mktemp`.

## Job `k8s-manifests`

**Co robi.** `kubeconform` czyta z każdego pliku `apiVersion` i `kind`, pobiera schemat JSON tego typu obiektu i porównuje plik ze schematem. Schematy pochodzą ze specyfikacji OpenAPI Kubernetesa.

**Flagi:**

- `-strict`: pole, którego nie ma w schemacie, jest błędem. Łapie literówki w nazwach pól, np. `replcias`.
- `-kubernetes-version 1.36.1`: schematy dokładnie tej wersji, którą ma klaster kind (`terraform/variables.tf`).
- `-schema-location`: drugi adres to publiczny katalog schematów CRD. Stamtąd jest schemat dla `Application` z ArgoCD, którego nie ma w samym Kubernetesie.
- `-ignore-missing-schemas`: obiekt bez schematu jest pomijany zamiast oblewać job.
- `-summary -verbose`: wypisuje każdy plik i podsumowanie z licznikiem `Skipped`.

**Co łapie.** Zły typ wartości (`replicas: "trzy"` daje `got string, want null or integer`), nieznane pola, brak pól wymaganych.

**Czego nie łapie**, bo nie rozmawia z klastrem:

- Czy obraz z `image:` istnieje.
- Czy Secret z `secretKeyRef` albo ConfigMap z `volumes` istnieje.
- Czy `selector` w Service trafia w etykiety jakiegoś poda.
- Czy admission webhook albo polityka w klastrze nie odrzuci obiektu.
- Czy pod po starcie w ogóle działa.

**Słabe miejsce.** Przez `-ignore-missing-schemas` literówka w `kind` (np. `Deploymnet`) nie oblewa joba. Obiekt nie ma schematu, więc jest pomijany, a kod wyjścia to 0. Widać to tylko w podsumowaniu jako `Skipped: 1`. W poprawnym stanie repo ma być `Skipped: 0`.

**Różnica wobec `kubectl apply`.**

| | kubeconform | `kubectl apply --dry-run=server` | `kubectl apply` |
|---|---|---|---|
| Potrzebuje klastra | nie | tak | tak |
| Sprawdza schemat | tak | tak | tak |
| Admission i polityki klastra | nie | tak | tak |
| Zmienia coś w klastrze | nie | nie | tak |

**Lokalnie:**

```bash
kubeconform -strict -ignore-missing-schemas -kubernetes-version 1.36.1 \
  -schema-location default \
  -schema-location 'https://raw.githubusercontent.com/datreeio/CRDs-catalog/main/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json' \
  -summary -verbose k8s/ argocd/
```

## Job `docker-build`

**Co robi.**

1. `hadolint` sprawdza `python-apps/Dockerfile` pod kątem dobrych praktyk.
2. `docker/setup-buildx-action` włącza BuildKit z obsługą cache.
3. `docker/build-push-action` buduje obraz z `push: false`.

**Po co build bez pusha.** Żeby wiedzieć, że Dockerfile i `requirements.txt` nadal dają obraz. Pipeline nie ma dostępu do żadnego rejestru i go nie potrzebuje.

**Cache.** `cache-from: type=gha` i `cache-to: type=gha,mode=max` trzymają warstwy obrazu w cache GitHub Actions. Kolejny build pobiera gotowe warstwy i przebudowuje tylko to, co się zmieniło. `mode=max` zapisuje też warstwy etapu `builder`, a nie tylko końcowego obrazu.

**Co hadolint znalazł w tym repo** (naprawione):

- `DL3066`: `USER exporter` zamieniony na `USER 10001:10001`. Przy nazwie Kubernetes nie umie sprawdzić `runAsNonRoot` bez czytania `/etc/passwd` z obrazu.
- `DL3025`: `HEALTHCHECK CMD` zapisany jako tablica JSON. Polecenie startuje bez powłoki `sh` pośrodku.

**Czego nie łapie.** Podatności w obrazie bazowym i w pakietach (do tego służy skaner, np. Trivy). Nie sprawdza też, czy kontener po starcie działa.

**Lokalnie:**

```bash
docker run --rm -i hadolint/hadolint:v2.15.1 < python-apps/Dockerfile
DOCKER_BUILDKIT=1 docker build -t monitoring-exporter:local python-apps/
```

## Job `terraform`

**Co robi**, wszystko w katalogu `terraform/`:

1. `terraform fmt -check -recursive -diff`: sprawdza formatowanie. Niczego nie poprawia, tylko zwraca błąd i pokazuje różnicę.
2. `terraform init -backend=false -input=false`: pobiera providera `tehcyx/kind` w wersji z `.terraform.lock.hcl`. `-backend=false` znaczy, że nie dotyka żadnego stanu.
3. `terraform validate`: sprawdza składnię i spójność, np. czy każda użyta zmienna istnieje i czy argumenty zasobu pasują do providera.

**Czego nie łapie.** `validate` nie robi `plan`. Nie łączy się z Dockerem ani z kind, więc nie powie, czy klaster da się utworzyć.

**Lokalnie:**

```bash
cd terraform
terraform fmt -check -recursive -diff
terraform init -backend=false -input=false
terraform validate
```

## Czego w pipeline nie ma

- Testów reguł alertów (`promtool test rules`).
- Skanowania obrazu pod kątem podatności.
- Testu na prawdziwym klastrze (np. kind w CI i `kubectl apply`).
- Sprawdzania skryptów bash w `scripts/` (shellcheck).
