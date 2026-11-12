# journal.md — журнал попыток (append-only)

Агент читает этот файл ЦЕЛИКОМ перед каждой попыткой.
Формат записи — после таблицы; новые записи — в конец файла.

## Champion

- metric: <not measured yet>
- commit: <baseline>
- note: <baseline>

## Записи

| N | date | hypothesis | metric_before | metric_after | verdict | commit |
|---|------|------------|---------------|--------------|---------|--------|

<!-- Формат свободного комментария к записи (append после таблицы):
### N — <гипотеза>
- files: <что правил>
- diff: <1 строка>
- note: <почему keep/revert>
-->
