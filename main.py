from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from stockData import get_stock_prices
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas


app = Flask(__name__)
app.config['SECRET_KEY'] = 'ldnumdc%^Yd34^Ugw2BN*4drg'
Bootstrap(app)


# *************** CREATE GET STOCK DATA FORM *****************

class GetStockData(FlaskForm):
    ticker = StringField('Stock Ticker', validators=[DataRequired()])
    start_date = StringField('Start Date (mm/dd/yyyy)', validators=[DataRequired()])
    end_date = StringField('End Date (mm/dd/yyyy)', validators=[DataRequired()])

    submit = SubmitField("Get Data")



@app.route("/")
def home():


    return render_template('index.html')

@app.route("/stockdata", methods=['GET', 'POST'])
def get_stock_data():

    form = GetStockData()

    if form.validate_on_submit():
        ticker = form.ticker.data
        start = form.start_date.data
        end = form.end_date.data
        df = get_stock_prices(ticker, start, end)

        fig = plt.plot(df.index, df.Close, color='red')

        output = io.BytesIO()
        plot = FigureCanvas(fig).print_png(output)
        # plot = Response(output.getvalue(), mimetype='image/png')


        return render_template('chart.html', tick=ticker, plot=plot)


    return render_template('search.html', form=form)




if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)