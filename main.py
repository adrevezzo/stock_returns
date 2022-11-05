from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from stockData import StockData
import base64
from io import BytesIO
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import pandas as pd
import os



app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap(app)


# *************** CREATE GET STOCK DATA FORM *****************

# class GetStockData(FlaskForm):
#     ticker = StringField('Stock Ticker', validators=[DataRequired()])
#     start_date = StringField('Start Date (mm/dd/yyyy)', validators=[DataRequired()])
#     end_date = StringField('End Date (mm/dd/yyyy)', validators=[DataRequired()])
#     ret_period = StringField('Return Period (days)', validators=[DataRequired()])
#
#     submit = SubmitField("Get Data")



@app.route("/", methods=['GET', 'POST'])
def home():

    # form = GetStockData()

    if request.method == "POST":
        data = request.form
        ticker = data['ticker']
        start = data['start_date']
        end = data['end_date']
        ret_per = int(data['ret_period'])

        # Create instance of StockData
        stock = StockData(ticker.upper())

        #Get Live Price
        cur_price = stock.cur_price

        # Get Historical Prices
        df = stock.get_historical_prices(start, end)

        df2, stdev, mean, nf_conf, nf_per, skew = stock.calc_returns(df=df, day_offset=ret_per)


        # Generate the figure **without using pyplot**.
        fig = Figure(facecolor='#d1d1d1')
        ax1, ax2 = fig.subplots(2,1)

        # Create Price Action Chart
        ax1.set_title(f'{ticker.upper()} Closing Prices from {start} through {end}')
        ax1.plot(df.index, df['Adj Close'], color='#7AD9FF')


        # ax2.set_title(f'Mean return is: {mean * 100: .2f}%\nLower 98% Conf return is: {nf_conf * 100: .2f}%'
        #               f'\n 98% Percentile return is: {nf_per * 100: .2f}%')

        ax2.set_title(f'Distribution of {ret_per} Day Returns (Skew = {skew: .3f})')
        ax2.hist(df2['returns'], bins=30, color='lightsalmon', ec='black')

        fig.tight_layout()

        # Convert plot to PNG image
        pngImage = BytesIO()
        FigureCanvas(fig).print_png(pngImage)

        # Encode PNG image to base64 string
        img = "data:image/png;base64,"
        img += base64.b64encode(pngImage.getvalue()).decode('utf8')

        stats_df = pd.DataFrame((stdev, mean, nf_conf, nf_per, ret_per),
                                index=['stdev', 'mean', 'nf_conf', 'nf_per', 'ret_per'],
                                columns=['stats'])

        return render_template('chart.html', tick=ticker, plot=img, cur_price=cur_price, stats=stats_df)



    return render_template('index.html')#, form=form)

@app.route("/stockdata", methods=['GET', 'POST'])
def get_stock_data():


    return render_template('search.html', form=form)

@app.route("/blog")
def blog():

    return render_template('blog.html')


@app.route("/login")
def login():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)