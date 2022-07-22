import data

rawData = data.Data()

while True:
    plot_type = input('==> Do you want a Scatter Plot (1), Line Graph (2), or to quit (q)? ')
    if plot_type.lower() == 'q':
        break

    tag = input('==> What tag do you want to see plotted? ')
    start_date = input('==> What is the start date? ')
    end_date = input('==> What is the end date? ')

    if start_date == '':
        start_date = None
    if end_date == '':
        end_date = None

    match plot_type:
        case '1':
            trend_line = input('==> What type of trend line do you want? (Press ENTER for no trend line)\n'
                                   ' 1. ols\n'
                                   ' 2. lowess\n'
                                   ' 3. ewm (Not Working)\n' # ToDo: figure out why these plots are not working
                                   ' 4. rolling\n'
                                   ' 5. expanding (Not Working)\n'
                                   '==> ')
            match trend_line:
                case '':
                  trend = None
                case '1':
                   trend = 'ols'
                case '2':
                   trend = 'lowess'
                case '3':
                   trend = 'ewm'
                case '4':
                   trend = 'expanding'
                case _:
                    trend = None

            plot = rawData.makeScatterPlotByTag(tag, trend=trend)

        case '2':
            plot = rawData.makeLineChart(tag, start_date='01/01/2020', end_date='01/01/2022')
        case _:
            break

    plot.show()

