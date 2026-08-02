# Job RADAR

**Job RADAR** — portfolio-ready Data Engineering проект для сбора, обработки, хранения и анализа данных о вакансиях.

Проект реализует полный multi-source data pipeline:

```text
Job APIs
   ↓
Extraction
   ↓
Raw Storage
   ↓
Normalization
   ↓
Data Quality
   ↓
Multi-source Combination
   ↓
Deduplication
   ↓
ClickHouse
   ↓
Analytical Marts
   ↓
Apache Superset
```

Основной фокус проекта — Data Engineering: надёжный ingestion, единая модель данных, разделение storage layers, оркестрация, аналитические витрины и воспроизводимая обработка данных.

---

## Dashboard

Job RADAR включает аналитический dashboard в Apache Superset, построенный поверх витрин ClickHouse.

На текущий момент dashboard показывает:

- общее количество вакансий;
- количество уникальных компаний;
- количество обнаруженных технических навыков;
- количество remote-вакансий;
- динамику рынка вакансий;
- соотношение remote / non-remote;
- компании с наибольшим количеством вакансий;
- наиболее популярные локации вакансий.

![Job RADAR Market Overview](docs/images/job_radar_market_overview.png)

---

## Текущий релиз

**Job RADAR v1.0.0**

Первая portfolio-ready версия включает:

- 3 источника вакансий;
- raw и processed data layers;
- S3-compatible object storage;
- единую canonical job schema;
- проверки качества данных;
- объединение данных из нескольких источников;
- cross-source deduplication;
- аналитическое хранилище ClickHouse;
- 7 аналитических витрин;
- оркестрацию через Airflow;
- dashboard в Apache Superset.

---

# Источники данных

Текущий pipeline собирает вакансии из:

- **Arbeitnow**
- **RemoteOK**
- **Jooble**

Каждый источник реализован как отдельный независимый extractor.

Extractor выполняет полный source-specific workflow:

```text
API request
    ↓
Fail-fast validation ответа
    ↓
Сохранение raw JSON
    ↓
Загрузка raw-данных в MinIO
    ↓
Создание batch_id
    ↓
Normalization
    ↓
Quality checks
    ↓
Сохранение processed CSV
    ↓
Загрузка processed-файла в MinIO
    ↓
Возврат pandas DataFrame
```

Такой подход позволяет изолировать особенности конкретного API, сохраняя единый формат данных на выходе.

---

# Архитектура

```text
                ┌─────────────┐
                │ Arbeitnow   │
                └──────┬──────┘
                       │
                ┌─────────────┐
                │ RemoteOK    │
                └──────┬──────┘
                       │
                ┌─────────────┐
                │ Jooble      │
                └──────┬──────┘
                       │
                       ▼
              Source Extractors
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
         Raw JSON          Source Normalization
             │                   │
             ▼                   ▼
           MinIO           Quality Checks
                                 │
                                 ▼
                          Processed CSV
                                 │
                                 ▼
                               MinIO
                                 │
                                 ▼
                      Normalized DataFrames
                                 │
                                 ▼
                     Combine Normalized Batches
                                 │
                                 ▼
                          Deduplication
                                 │
                                 ▼
                            ClickHouse
                                 │
                                 ▼
                        Analytical Marts
                                 │
                                 ▼
                         Apache Superset
```

---

# Единая схема вакансии

Все источники нормализуются в одну canonical schema:

```text
batch_id
source
source_job_id
title
company
location_raw
country
remote
url
tags
skills
created_at
extracted_at
description
```

ClickHouse loader дополнительно добавляет:

```text
loaded_at
```

Итоговая схема таблицы в ClickHouse:

```text
batch_id
source
source_job_id
title
company
location_raw
country
remote
url
tags
skills
created_at
extracted_at
description
loaded_at
```

---

# Слои хранения данных

## Raw Layer

Оригинальные ответы API сохраняются в JSON без изменения исходной структуры.

Локально:

```text
data/raw/
```

В MinIO:

```text
raw/
└── source=<source>/
    └── dt=<YYYY-MM-DD>/
```

Raw-данные сохраняются до normalization, чтобы исходный ответ API можно было проверить, повторно обработать или использовать при отладке.

---

## Processed Layer

Нормализованные данные сохраняются в CSV.

Локально:

```text
data/processed/
```

В MinIO:

```text
processed/
└── source=<source>/
    └── dt=<YYYY-MM-DD>/
```

Все processed-файлы соответствуют canonical schema Job RADAR.

---

# Multi-source Processing

Каждый extractor возвращает нормализованный pandas DataFrame.

Основной pipeline собирает их в список:

```python
normalized_batches = [
    run_arbeitnow(),
    run_remoteok(),
    run_jooble(),
]
```

Затем данные объединяются перед загрузкой в ClickHouse:

```text
normalized DataFrames
        ↓
pd.concat()
        ↓
deduplication
        ↓
schema validation
        ↓
ClickHouse
```

Текущая дедупликация удаляет точные дубли на основе стабильных идентификаторов и нормализованных URL.

Более сложный fuzzy matching намеренно не входит в scope версии v1.0.

---

# ClickHouse

ClickHouse используется как основная аналитическая база данных.

Database:

```text
job_radar
```

Основная таблица:

```text
jobs
```

Таблица использует `ReplacingMergeTree`, что позволяет удобно работать с повторными загрузками pipeline и сохранять простую аналитическую модель.

Перед вставкой loader:

1. принимает объединённый DataFrame;
2. добавляет `loaded_at`;
3. проверяет canonical schema;
4. приводит list-like колонки к нужному типу;
5. загружает batch в ClickHouse.

Для отладки и восстановления loader также можно запускать вручную по последнему processed CSV.

---

# Аналитические витрины

В Job RADAR v1.0 реализовано семь ClickHouse marts.

## `skills_mart`

Аналитика востребованности навыков:

```text
skill
vacancies
remote_vacancies
non_remote_vacancies
unique_companies
```

---

## `remote_mart`

Соотношение remote и non-remote вакансий:

```text
work_format
vacancies
unique_companies
```

---

## `companies_mart`

Аналитика по компаниям:

```text
company
vacancies
remote_vacancies
non_remote_vacancies
unique_skills
```

---

## `locations_mart`

Аналитика по исходным локациям:

```text
location_raw
vacancies
remote_vacancies
non_remote_vacancies
unique_companies
```

---

## `skill_pairs_mart`

Часто встречающиеся комбинации технологий:

```text
skill_1
skill_2
vacancies
remote_vacancies
unique_companies
```

---

## `daily_snapshot_mart`

Ежедневные снимки состояния рынка вакансий:

```text
snapshot_date
total_vacancies
remote_vacancies
non_remote_vacancies
unique_companies
unique_skills
```

---

## `daily_country_mart`

Ежедневная аналитика по странам:

```text
snapshot_date
country
vacancies
non_remote_vacancies
onsite_vacancies
unique_companies
```

---

# Airflow

Apache Airflow используется для оркестрации pipeline.

Executor:

```text
LocalExecutor
```

Metadata database:

```text
PostgreSQL
```

Текущий DAG:

```text
job_radar_pipeline
```

DAG запускает полный Job RADAR pipeline по расписанию.

Application pipeline выполняет:

```text
Extract and normalize sources
        ↓
Combine normalized batches
        ↓
Deduplicate
        ↓
Load to ClickHouse
        ↓
Refresh analytical marts
```

Retries и ограничения на одновременные запуски настроены на уровне DAG.

---

# Dashboard

Apache Superset подключается напрямую к аналитическому слою ClickHouse.

Текущий dashboard:

```text
Job RADAR — Market Overview
```

В нём реализованы:

### KPI

- Total Vacancies
- Unique Companies
- Detected Skills
- Remote Vacancies

### Аналитические графики

- Job Market Trend
- Remote vs Non-Remote
- Top Companies by Vacancies
- Top Job Locations

Dashboard специально работает с аналитическими витринами, а не повторяет бизнес-логику напрямую поверх таблицы `jobs`.

---

# Технологический стек

## Data Engineering

- Python 3.12
- pandas
- requests
- python-dotenv
- boto3
- clickhouse-connect

## Infrastructure

- Docker
- Docker Compose

## Object Storage

- MinIO
- S3-compatible storage layout

## Analytical Database

- ClickHouse

## Orchestration

- Apache Airflow 2.9.3
- LocalExecutor
- PostgreSQL

## Analytics / BI

- Apache Superset

## Development

- uv
- Git
- GitHub

---

# Структура проекта

```text
de_job_radar/
│
├── airflow/
│   ├── dags/
│   │   └── job_radar_pipeline_dag.py
│   ├── config/
│   ├── logs/
│   └── plugins/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── docs/
│   ├── images/
│   │   └── job_radar_market_overview.png
│   ├── troubleshooting/
│   ├── architecture.md
│   ├── CURRENT_STATE.md
│   └── roadmap.md
│
├── sql/
│   ├── basic_analysis.sql
│   └── clickhouse/
│       ├── create_tables/
│       └── refresh_marts/
│
├── src/
│   ├── extractors/
│   │   ├── e_arbeitnow.py
│   │   ├── e_remoteok.py
│   │   └── e_jooble.py
│   │
│   ├── normalizers/
│   │   ├── common.py
│   │   ├── n_arbeitnow.py
│   │   ├── n_remoteok.py
│   │   └── n_jooble.py
│   │
│   ├── loaders/
│   │   ├── clickhouse_loader.py
│   │   ├── create_clickhouse_schema.py
│   │   └── refresh_marts.py
│   │
│   ├── pipelines/
│   │   ├── run_jobs_pipeline.py
│   │   └── combine_normalized_batches.py
│   │
│   └── utils/
│       ├── clickhouse.py
│       ├── jobs_schema.py
│       ├── quality.py
│       └── s3.py
│
├── Dockerfile.airflow
├── docker-compose.yml
├── docker-compose.airflow.yml
├── requirements.txt
├── .env.example
├── README.md
└── README_RU.md
```

---

# Запуск проекта

## 1. Установка Python dependencies

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

---

## 2. Настройка переменных окружения

Создать:

```bash
cp .env.example .env
```

После этого заполнить необходимые API keys и параметры инфраструктуры.

Файл `.env` не должен попадать в Git.

---

## 3. Запуск MinIO и ClickHouse

```bash
docker compose up -d
```

Проверка:

```bash
docker compose ps
```

---

## 4. Ручной запуск полного pipeline

```bash
uv run python -m src.pipelines.run_jobs_pipeline
```

Pipeline выполнит:

```text
extract
→ normalize
→ store
→ combine
→ deduplicate
→ load
→ refresh marts
```

---

## 5. Запуск отдельного источника

Примеры:

```bash
uv run python -m src.extractors.e_arbeitnow
uv run python -m src.extractors.e_remoteok
uv run python -m src.extractors.e_jooble
```

---

## 6. Запуск Airflow

```bash
docker compose -f docker-compose.airflow.yml up -d
```

Airflow UI:

```text
http://localhost:8080
```

---

## 7. Analytics Dashboard

Apache Superset используется как BI layer и подключается к базе ClickHouse проекта Job RADAR.

Superset UI в локальной среде разработки:

```text
http://localhost:8088
```

---

# Data Quality

Текущие проверки качества данных включают:

- отсутствие title;
- отсутствие URL;
- duplicate URLs;
- вакансии без определённых skills;
- фильтрацию строк без обязательных полей;
- валидацию canonical schema перед загрузкой в ClickHouse;
- exact deduplication при объединении нескольких источников.

Для неожиданных структур API response используется fail-fast подход.

---

# Архитектурные принципы

Job RADAR намеренно избегает ненужного усложнения.

Текущие принципы:

- каждый source extractor является независимым модулем;
- source-specific normalization изолирована;
- все источники возвращают одну canonical schema;
- SQL-аналитика отделена от Python-кода;
- ClickHouse marts обслуживают BI-слой;
- orchestration отделена от business logic;
- изменения внедряются небольшими проверяемыми шагами.

Проект намеренно не использует сложные extractor factories, inheritance hierarchy или plugin framework.

---

# Roadmap

Версия `v1.0.0` представляет первую завершённую portfolio-ready версию проекта.

Дальнейшее развитие описано в:

```text
docs/roadmap.md
```

Основные направления:

- ATS integrations;
- улучшение normalization;
- усиление automated testing;
- source-level failure isolation;
- monitoring и alerting;
- deployment;
- advanced deduplication;
- расширение dashboard analytics.

---

# Статус

**v1.0.0 — portfolio-ready release candidate**

Основной Data Engineering pipeline и первый аналитический dashboard завершены.

После финальной проверки документации проект готов к созданию Git tag `v1.0.0` и публикации первого GitHub Release.
