# autoresearch — RSI-цикл этого репо

Канон: `C:\git\github-projects-workflow\docssi-autoresearch.md`.
Скилл исполнителя: `rsi-loop` (глобальный, `~/.agents/skills/rsi-loop`).

Цикл: одна правка внутри `scope.md` → `eval/run_eval` возвращает ОДНО
число → лучше `## Champion` = коммит, хуже = откат → запись в
`journal.md`. Правила: одна метрика · сейф (eval read-only, holdout
закрыт гейтом) · маленькие шаги · журнал · бюджет.

## Старт цикла

1. Человек заполняет `program.md` (цель, метрика, идеи, рамки).
2. `eval/run_eval.*` реально печатает число (контракт — `eval/README.md`).
3. `budget.md` — лимиты и стоп-условия.
4. Запуск: «запусти rsi-loop» в сессии агента, или `/loop <интервал>
   rsi-loop`. Стоп — по `budget.md` или по команде.

## Сейф

`eval/` и `holdout/` защищены PreToolUse-гейтом
(`.devin/scripts/rsi_safe_gate.py`, подключён в `.devin/hooks.v1.json`):
агент может ЗАПУСКАТЬ run_eval, но не править eval/ и не читать
holdout/. Обход гейта через exec = нарушение канона.
