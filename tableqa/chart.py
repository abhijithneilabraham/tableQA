import pandas as pd
import matplotlib.pyplot as plt
import matplotlib


class Chart:
    """
    Generates chart for the results.

    Attributes
    ----------
    __REGISTERED_CHARTS: `dictionary` object.
        Information about the available chart types to visualize the results.
    figsize: `tuple`
        Figure size of the plot.

    Methods
    -------
    registered_charts()
        Adds new chart type to the registered charts.
    """
    def __init__(self, ctypes, query, answers, size):
        """
        Constructs the necessary attributes and calls the correct function to construct output chart.

        Arguments
        ----------

        ctypes: `str` or `list` object
                specify the chart types.
        query: `str`
                query used to fetch output from the database.
        answers: `list`
                Output for the query.
        size: `tuple`
                figure size of the chart.
        """
        if len(answers) == 0:
            return

        self.registered_charts()

        if not isinstance(size, tuple):
            import warnings
            warnings.warn('Argument `size` should be of the form tuple. Example - size=(20, 20)')
            return
        self.figsize = size

        # fetch column names
        columns = query.split('SELECT')[-1].split('FROM')[0]
        columns = columns.split(',')

        # fetch answer names
        answers = list(map(list, list(zip(*answers))))
        assert(len(columns) == len(answers))

        if isinstance(ctypes, list):
            for ctype in ctypes:
                if ctype.lower() not in self.__REGISTERED_CHARTS:
                    import warnings
                    warnings.warn('The only supported chart types are - {}. Please select one of the two to visualize your results.'.format(list(self.__REGISTERED_CHARTS.keys())))
                else:
                    getattr(self, ctype.lower())(columns, answers)
        elif ctypes.lower() == 'all':
            for ctype in self.__REGISTERED_CHARTS:
                getattr(self, ctype)(columns, answers)
        else:
            if ctypes.lower() not in self.__REGISTERED_CHARTS:
                import warnings
                warnings.warn('The only supported chart types are - {}. Please select one of the two to visualize your results.'.format(list(self.__REGISTERED_CHARTS.keys())))
            else:
                getattr(self, ctypes.lower())(columns, answers)

    def registered_charts(self):
        """
        Add new chart type to the registered charts.
        """
        self.__REGISTERED_CHARTS = dict()
        self.__REGISTERED_CHARTS['bar'] = '__bar'
        self.__REGISTERED_CHARTS['pie'] = '__pie'

    def __pie(self, columns, answers):
        """
        Function that returns a pie chart.

        # Arguments

        columns: `list` object, column names.
        answers: `list` object, corresponding answer values.
        """
        for i, colname in enumerate(columns):
            answer = answers[i]
            if len(answer) == 1:
                import warnings
                warnings.warn('Cannot plot chart for a single value.')
                break
            plt.figure(figsize=self.figsize)
            answer = pd.DataFrame(answer, columns=[colname])
            grouped_col = answer[colname].value_counts()
            ax = grouped_col.plot(kind='pie', startangle=0, autopct='%.2f', title=colname, fontsize=10, labels=None)
            ax.yaxis.set_label_coords(-0.15, 0.5)
            ax.axis("off")
            ax.set_title('Distribution of ' + colname, fontsize=15)                   # set title
            plt.legend(grouped_col.index, bbox_to_anchor=(1, 0.5), loc="center right", fontsize=10, bbox_transform=plt.gcf().transFigure)
            plt.savefig('pie_' + str(colname).strip() + '.png', bbox_inches='tight')

    def __bar(self, columns, answers):
        """
        Function that returns a bar chart.

        # Arguments

        columns: `list` object, column names.
        answers: `list` object, corresponding answer values.
        """
        for i, colname in enumerate(columns):
            answer = answers[i]
            if len(answer) == 1:
                import warnings
                warnings.warn('Cannot plot chart for a single value.')
                break
            answer = pd.DataFrame(answer, columns=[colname])

            # if it is a numeric value.
            if answer[colname].astype(str).str.isnumeric().all():
                plt.figure(figsize=self.figsize)
                ax = answer.hist(column=colname)
                ax = ax[0]
                for x in ax:
                    x.grid(False)                                               # remove the plot grid
                    x.spines['right'].set_visible(False)                        # despine
                    x.spines['top'].set_visible(False)
                    x.spines['left'].set_visible(False)
                    x.set_title('Distribution of ' + colname, fontsize=15)        # set title                                           
            else:
                plt.figure(figsize=self.figsize)
                grouped_col = answer[colname].value_counts()
                ax = grouped_col.plot.bar(y=colname)
                ax.set_xlabel(colname, labelpad=20, weight='bold', size=12)     # set column label
                ax.set_title('Distribution of ' + colname, fontsize=15)           # set title
            plt.savefig('bar_' + str(colname).strip() + '.png', bbox_inches='tight')
