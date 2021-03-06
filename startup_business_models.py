## Imports
import urllib
import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html

import urllib.request
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from urllib.error import URLError
import requests
from googlesearch import search

import matplotlib.pyplot as plt
from math import e

st.set_page_config(page_title="Eikona: AR-Based NFT Gaming Startup", page_icon=":100:", layout="wide",initial_sidebar_state="expanded")
eikona_choice = option_menu("Eikona: AR-Based NFT Gaming Startup", ["Industry User Growth", "Business Model Basics"],
                        icons=['activity', '123'],
                        menu_icon="calculator", default_index=0, orientation="horizontal",
                        styles={
    "container": {"padding": "5!important", "background-color": "#BBBBBD"},
    "icon": {"color": "white", "font-size": "25px"}, 
    "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
    "nav-link-selected": {"background-color": "#BBBBBD"},})

##data
coinbase_users_historic = pd.read_csv("https://raw.githubusercontent.com/maxwellknowles/eikona/main/coinbase_users.csv")
pokemongo_users = pd.read_csv("https://raw.githubusercontent.com/maxwellknowles/eikona/main/pg_users.csv")

#####
##Variables/Default values - PreCache
#####

###Calculating TPM
interval_of_users = 50
p_coefficient = float(0.006)
q_coefficient = float(0.410)

#Define Bass Diffusion Model Function first here for efficiency
def get_bass_model(p, q, M, period = 30):

    # Initializing the arrays
    A = [0] * period
    R = [0] * period
    F = [0] * period
    N = [0] * period

    # One important thing to note, is that the time period we start from is t = 0.
    # In many articles, you will see time starting from t = 1. They are both the
    # same for all intents and purposes. Starting with t = 0 makes life easier in
    # python, as indexing in python starts from 0 too.

    # We start with A(0) =0, and build up the values for t = 0 from the equations
    # formulated
    A[0] = 0
    R[0] = M
    F[0] = p
    N[0] = M*p

    # Recursion starts from next time step
    t = 1

    # Creating a helper function for recursion
    def get_bass_model_helper(A, R, F, N, t):

        # If we have reached the final period, return the values
        if t == period:
            return N, F, R, A
        else:

            # Else, just compute the values for t
            A[t] = N[t-1] + A[t-1]
            R[t] = M - A[t]
            F[t] = p + q * A[t]/M
            N[t] = F[t] * R[t]

            # compute values for the next time step
            return get_bass_model_helper(A, R, F, N, t+1)

    N, F, R, A = get_bass_model_helper(A, R, F, N, t)

    # Converting to numpy arrays and returning.
    return np.array(N), np.array(A)

#-------------------------
#Business Model
#-------------------------
if eikona_choice == "Industry User Growth":
    st.title("Industry User Growth")
    st.header('_Crypto & AR-Gaming_')

    col1, col2 = st.columns(2)

    #################
    ###Industry Growth
    # Coinbase YoY -- millions
    ###Changeables/Sliders:
    # - Estimated YoY Growth% from 2022 Onward
    #################

    with col1:
        cb_historic_rate = ((coinbase_users_historic['Coinbase Users'][len(coinbase_users_historic)-1]-coinbase_users_historic['Coinbase Users'][0])/coinbase_users_historic['Coinbase Users'][0])/8
        cb_historic_rate = str(round(cb_historic_rate*100))+" %"
        st.write('Coinbase Average Annual User Growth (2014-2021):', cb_historic_rate)
        cb_growth = st.slider('Estimated YoY Growth (%) for Coinbase Users from 2022 Onward...', -100, 1000, 100)
        cb_growth = cb_growth*0.01
        l   = []
        for i in range(1,5):
            year = str(2021+i)
            cb_users = round(56*(1+cb_growth)**i)
            tup=(year, cb_users)
            l.append(tup)
        cb_projected = pd.DataFrame(l, columns=['Year','Coinbase Users'])
        coinbase_users = coinbase_users_historic.append(cb_projected, ignore_index=True)
        l = []
        for i in coinbase_users.iterrows():
            year = datetime.strptime(str(i[1]['Year']),"%Y")
            cb_users = i[1]['Coinbase Users']
            tup=(year, cb_users)
            l.append(tup)
        coinbase_users = pd.DataFrame(l, columns=['Year','Coinbase Users'])
        coinbase_users = coinbase_users.set_index('Year')


        st.subheader('Coinbase Users (in millions)')
        st.line_chart(coinbase_users)

    #################
    ###Industry Growth
    # Pokemon YoY -- millions
    ###Changeables/Sliders:
    # - Estimated YoY Growth% from 2022 Onward
    #################

    with col2:
        pg_historic_rate = ((pokemongo_users['PG Users'][len(pokemongo_users)-1]-pokemongo_users['PG Users'][1])/pokemongo_users['PG Users'][1])/4
        pg_historic_rate = str(round(pg_historic_rate*100))+" %"
        st.write('Pokemon GO Average Annual User Growth (2017-2020):', pg_historic_rate)
        pg_growth = st.slider('Estimated YoY Growth (%) for Pokemon GO Users from 2021 Onward...', -100, 1000, 40)
        pg_growth = pg_growth*0.01
        l = []
        for i in range(1,6):
            year = str(2020+i)
            pg_users = round(166*(1+pg_growth)**i)
            tup=(year, pg_users)
            l.append(tup)
        pg_projected = pd.DataFrame(l, columns=['Year','PG Users'])
        pokemongo_users = pokemongo_users.append(pg_projected, ignore_index=True)
        l = []
        for i in pokemongo_users.iterrows():
            year = datetime.strptime(str(i[1]['Year']),"%Y")
            pg_users = i[1]['PG Users']
            tup=(year, pg_users)
            l.append(tup)
        pokemongo_users = pd.DataFrame(l, columns=['Year','PG Users'])
        pokemongo_users = pokemongo_users.set_index('Year')

        st.subheader('Pokemon GO Users (in millions)')
        st.line_chart(pokemongo_users)

    #-------------------------
    ###Business Model Sidebar -- Calculating TPM

    st.title('Bassian Diffusion: Exploring the Market Opportunity')

    col3, col4 = st.columns(2)

    with col3:
        image = "https://github.com/maxwellknowles/portfolio/raw/main/Diffusion-of-Innovation.png"
        st.image(image)

    with col4:
        st.write('**Bassian Diffusion of Innovaton Adoption** is a widely-accepted sociological phenomenon, successfully modeling the rate of adoption or growth for everything from Twitter trends to users of new devices.')
        st.write("Eikona is keen on understanding how the crypto space will evolve, what the ultimate market opportunity is, and how our unique positioning might unlock the most aggressive share of that market opportunity. As an exercise to evaluate crypto adoption, we've set the default values of the _p-coefficient_ (adoption), _q-coefficient_ (imitation), and industry size of the Bass model below to match the user adoption of Coinbase through 2021.")
        st.write("Based on this analysis, we believe we are only now transitioning from the **_early adopters_** to the **_early majority_**, making Eikona's method and mission of tackling widespread adoption through a _safe_, _simple_, and _fun_ experience not only unique, but _**timely**_. We are built for this moment.")

    st.subheader("Using Coinbase users as a proxy for crypto adoption in light of Bass diffusion...")
    col5, col6 = st.columns(2)

    with col5:
        #Setting Up Sliders
        industry_size = st.slider('Select Industry Size by 2040 (IN BILLIONS)', min_value = 0.1, max_value = 5.5,value = 1.0, step = 0.01)

        p_coefficient = st.slider('P Coefficient: Innovation', min_value = 0.001, max_value = 0.050, value = p_coefficient, step = 0.005)
        q_coefficient = st.slider('Q Coefficient: Imitation', min_value = 0.250, max_value = 0.550, value = q_coefficient, step = 0.005)
        period = st.slider('Period of time to predict until:', min_value = 10, max_value = 100, value = 25, step = 1)
        industry_size = 1000000000 * industry_size

        #col1 = st.columns(1)
        #with col1:

    with col6:

        fig = plt.figure()
        ax = plt.gca()

        #Pull in historic Coinbase user data and reformat for Bass graph
        coinbase_users_historic["Lifetime"] = coinbase_users_historic['Year']-2014
        coinbase_users_historic = coinbase_users_historic.drop("Year", 1)
        coinbase_users_historic["Users"] = coinbase_users_historic['Coinbase Users']*1000000
        coinbase_users_historic = coinbase_users_historic.drop("Coinbase Users", 1)

            #Plot Coinbase user data
        ax.plot(coinbase_users_historic['Lifetime'], coinbase_users_historic['Users'],'x', markersize=5)

            #Calling the function to get the new models
        N, A = get_bass_model(p_coefficient, q_coefficient, M=float(industry_size), period = period)

            #Creating Periods
        t = list(range(0, period))

            #Plotting Data and changing size of points
        ax.plot(t, N, 'o', markersize = 4)

            #Give it a cleaner look and remove the spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

            # Setting label and title
        ax.set_title('Adoption Count for p = {} and q = {}'.format(p_coefficient, q_coefficient))
        ax.set_ylabel("New Customers")
        ax.set_xlabel("Industry Lifetime (y)")

            # Creating a clean layout
        fig.tight_layout()

        st.pyplot(fig)

        users_t = coinbase_users_historic['Users'][7]
        t = coinbase_users_historic['Lifetime'][7]
        m = users_t * (p_coefficient/(p_coefficient+q_coefficient)**2) * (((1 + (q_coefficient/p_coefficient) * (e ** -(p_coefficient + q_coefficient)*t))**2) / (e ** -(p_coefficient+q_coefficient)*t))


if eikona_choice == "Business Model Basics":
    st.header("Business Model Basics")
    
    initial_people_involved = st.number_input('Number of initial players: ', min_value = 1, max_value = 100000000, value = 10000, step = 250)
    user_growth_rate = st.slider('Rate of User Growth/Year: 0.01 is equal to 1 percent of initial users', min_value = 0.01, max_value = 10.00, value = 1.00)
    avg_min_month = st.slider('Average Minutes Walked in AR/Month: ', min_value = 0, max_value = 600, value = 300, step = 10)
    st.write('_Equivalent to ' + str(float(avg_min_month/60)) + ' hours or ' + str(avg_min_month*60) + ' seconds_')
    #rate_per_sec_AR = st.slider('$EKO generated each second in AR ad-compatible space: ', min_value = 0.001, max_value = 5.0, value = 0.01)

    people_involved = initial_people_involved

    uot = []
    l = []
    for i in range(0,6):
        year = i
        uot_ = (initial_people_involved+(initial_people_involved * user_growth_rate*i))
        ar_ad_time = avg_min_month*uot_*12
        tup = (year, uot_, ar_ad_time)
        uot.append(uot_)
        l.append(tup)

    
    uot = pd.DataFrame(l, columns = ['Year', 'Users', 'AR Ad Time'])
    st.subheader('Toggle Revenue Basics')
    price_mint = st.slider('Estimated Price for User to Mint ($USD)...', 0.00, 10.00, 5.00, 0.25)
    #conversion_rate = st.slider('Estimated Share of Users Who Mint (%)...', 0, 100, 50)
    #conversion_rate = conversion_rate*0.01
    ar_ad_cpm = st.slider('Estimated Avg Number of Exchanges In-Game', 0, 50, 10)
    transaction_cost = st.slider('Transaction Fee ($USD)...', 0.00, 5.00, 0.25, 0.05)
    st.subheader('Toggle Cost Basics')
    cost_mint = st.slider('Estimated Cost of User to Mint ($)...', 0.00, 5.00, 0.25, 0.05)
    server_cost = st.slider('Estimated Server Costs/Month (Per User in $)...', 0.00, 5.00, 3.00, 0.10)

    l = []
    for i in uot.iterrows():
        year = float(i[1]['Year'])
        users = i[1]['Users']
        ad_time = i[1]['AR Ad Time']
        revenue = users*price_mint + users*ar_ad_cpm*transaction_cost
        costs = cost_mint*users + server_cost*users*(year/12)
        tup=(year, users, ad_time, revenue, costs)
        l.append(tup)
    eikona_business = pd.DataFrame(l, columns=['Year','Users', 'AR Ad Time', 'Revenue ($USD)', 'Costs'])
    eikona_business = eikona_business.set_index("Year")
    eikona_user_and_revenue = eikona_business[['Users','Revenue ($USD)', 'Costs']]
    eikona_ad_time = eikona_business[['AR Ad Time']]
    st.subheader("Eikona Game Revenue, Cost, and Users By Year")
    st.area_chart(eikona_user_and_revenue)
    st.subheader("Eikona Estimated Ad Time By Year")
    st.area_chart(eikona_ad_time)
    

