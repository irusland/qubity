# test_assignment

## Описание

В качестве тестового задания наша команда предлагает небольшую, но реальную задачку,
которая возникла перед нами
некоторое время назад. В рамках этой задачи у Вас будет возможность познакомиться с
двумя базовыми сущностями
криптоторговли: свечки (способ агрегации временных рядов) и перпетуальные контракты (тип
инструментов = бесконечные
фьючерсы).

Суть задания очень проста: представьте, что у нас есть все сделки на бирже, произошедшие
за последние сутки. Работать
со всеми трейдами сразу не очень осмысленно: данных много (~10 млн. строк), а что самое
главное они чрезмерно избыточны.
Традиционно их агрегируют в свечки - это тип данных, которые содержит базовые знания о
трейдах за фиксированный
промежуток времени (мы используем одну минуту). Вопрос, на который нужно ответить звучит
так: как лучше агрегировать
трейды в свечки?

Мы видим два лёгких подхода:

1) Написать на чистом Python код, который будет по очереди "слышать" трейды с биржи, а
   затем итеративно "обновлять"
   получающуюся свечку
2) Записать сначала все трейды в pandas.DataFrame, а затем работая встроенными методами
   для этой структуры данных,
   агрегировать данные в трейды

Нужно реализовать оба и посмотреть, есть разумный ли выигрыш в скорости, потреблении
памяти у одного подхода над
другим.

### Получение данных

Нужно напрямую из Binance научиться получать все открытые рыночные данные,
необходимые для формирования свечки.
Мы хотим формировать свечку для единственной монеты - Bitcoin, а для этого нужно будет
смотреть на две пары:

1) Спотовая пара BTC-USDT на бирже Binance
2) Перповая пара BTC-USDT на бирже Binance Futures

По каждой паре нужны сделки (trades), а для перпа нужны будут также open_interest и
funding_rate.

**Orderbook собирать не нужно!**

\* Если Вы не знакомы с тем, что это такое, прежде всего очень рекомендую разобраться.
Во-первых, это очень интересно,
а во-вторых, будет здорово понимать, что такое open_interest и funding_rate, чтобы смысл
задания был более понятен.

### Обработка данных

Полученные данные по сделкам, open_interest и funding_rate нужно привести в вид
агрегированных 1-минутных свечек.
Ожидается, что полученный dataframe будет выглядеть примерно как
в [файле](./processed_data/2024-07-21.feather).

Другими словами важно собрать следующие колонки:

| Название колонки | Для спота | Для перпа |
|------------------|-----------|-----------|
| _open_           | +         | +         |
| _high_           | +         | +         |
| _low_            | +         | +         |
| _close_          | +         | +         |
| _trades_         | +         | +         |
| _buy_trades_     | +         | +         |
| _sell_trades_    | +         | +         |
| _volume_         | +         | +         |
| _buy_volume_     | +         | +         |
| _sell_volume_    | +         | +         |
| _open_interest_  | na        | +         |
| _funding_rate_   | na        | +         |

Данную агрегацию просим выполнить двумя способами:
1) с использованием pandas/numpy, а именно resample/groupby;
2) и без использования pandas/numpy (чистый Python на циклах).

Примерно ожидаемые столбцы в агрегированной свечке:
[
'timestamp',
'open_spot',
'open_perp',
'high_spot',
'high_perp',
'low_spot',
'low_perp',
'close_spot',
'close_perp',
'volume_total',
'volume_spot',
'volume_perp',
'buy_volume_total',
'buy_volume_spot',
'buy_volume_perp',
'sell_volume_total',
'sell_volume_spot',
'sell_volume_perp',
'trades_total',
'trades_spot',
'trades_perp',
'buy_trades_total',
'buy_trades_spot',
'buy_trades_perp',
'sell_trades_total',
'sell_trades_spot',
'sell_trades_perp',
'open_interest',
'funding_rate',
]

### Результаты

Цель данной задачи - понять, достаточно ли хорошо pandas+numpy справляются с задачами,
чтобы даже на сложных операциях
оставаться быстрыми и легковесными, или же стоит написать агрегацию вручную, получив
прирост в скорости и уменьшив
потребление памяти.

### Прочие комментарии

- Мы не только приветствуем, но и настойчиво рекомендуем пользоваться LLM-моделей (
  ChatGPT, Claude и др.).
- Ожидается, что решение будет реализовано в виде Docker-образа и оно будет запускаться
  командой `docker-compose up`
- Пожалуйста, напишите хотя бы простейшие комментарии с пояснением общей архитектуры,
  результатов и отдельных строк кода.
- Когда у Вас получились агрегированные свечки, вы можете проверить их на сайте Binance
  или в TradingView
- Пожалуйста, при возникновении непонятностей - обращайтесь с вопросами. Что-то мы могли
  непонятно написать, с чем-то
  Вы может быть не сталкивались раньше.
