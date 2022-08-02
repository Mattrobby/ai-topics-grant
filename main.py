import data
import pandas as pd  # ToDo: remove this later
import plotly.express as px  # ToDo: remove this later
import json

rawData = data.Data(filters='taxnodes:Technology|Information Technology|Artificial Intelligence|Assistive Technologies')

test_type = 2

match test_type:
    case 1:  # plotting line and scatter plots
        while True:
            plot_type = input('==> Do you want a Scatter Plot (1), Line Graph (2), or to quit (q)? ')
            if plot_type.lower() == 'q':
                break

            target = input('==> What tag do you want to see plotted? ')
            start_date = input('==> What is the start date? ')
            end_date = input('==> What is the end date? ')

            if start_date == '':
                start_date = None
            if end_date == '':
                end_date = None

            match plot_type:
                case '1':
                    data = rawData.getAllTags()
                    data = rawData.getPlotDataByDate(data, target,
                                                     start_date=start_date, end_date=end_date)

                    trend_line = input('==> What type of trend line do you want? (Press ENTER for no trend line)\n'
                                       ' 1. ols\n'
                                       ' 2. lowess\n'
                                       ' 3. ewm (Not Working)\n'  # ToDo: figure out why these plots are not working
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

                    plot = rawData.makeScatterPlot(data, trend=trend)

                case '2':
                    plot = rawData.makeLineChart(data)
                case _:
                    break

            plot.show()
            print(plot)

    case 2:  # Plotting top x values
        data = rawData.getAllTags()
        count = 10
        start_date = '01/01/2019'
        end_date = None

        trend_options = dict(
            frac=0.1,
        )

        plot = rawData.plotTopX(data, count, 'scatter', trend_options=trend_options,
                         start_date=start_date, end_date=end_date)
        # plot.show()

        rawData.minMaxScaled(plot)

    case 3:  # Plotting Radar Chart
        rawData.plotTopX(rawData.getAllTaxNodes(), 5, plot_type='radar').show()