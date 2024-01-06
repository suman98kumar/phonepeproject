import requests
import pandas as pd
import numpy as np
import json
import psycopg2
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu

#SQL Connecter 
mydb=psycopg2.connect(host="localhost",    
                    user= "postgres",
                    password="Sugu1234",
                    database="phonepe_data",
                    port="5432")  #Connecting to SQL server 

cursor=mydb.cursor()

#Create a DataFrame from SQL

query='''select * from agg_trans'''
cursor.execute(query)
table1=cursor.fetchall()
mydb.commit()

Aggregated_Trans=pd.DataFrame(table1,columns=("States","Years","Quarter","Trans_Name","Trans_Count","Trans_Amount"))

query='''select * from agg_user'''
cursor.execute(query)
table2=cursor.fetchall()
mydb.commit()

Aggregated_User=pd.DataFrame(table2,columns=("States","Years","Quarter","User_Name","User_Count","User_Percentage"))

query='''select * from map_trans'''
cursor.execute(query)
table3=cursor.fetchall()
mydb.commit()

Map_Trans=pd.DataFrame(table3,columns=("States","Years","Quarter","Map_Dist","Map_Count","Map_Amount"))

query='''select * from map_user'''
cursor.execute(query)
table4=cursor.fetchall()
mydb.commit()

Map_User=pd.DataFrame(table4,columns=("States","Years","Quarter","Map_Dist","Map_Users","Map_Appopen"))

query='''select * from top_trans'''
cursor.execute(query)
table5=cursor.fetchall()
mydb.commit()

Top_Trans=pd.DataFrame(table5,columns=("States","Years","Quarter","Top_Dist","Top_Count","Top_Amount"))

query='''select * from top_user'''
cursor.execute(query)
table6=cursor.fetchall()
mydb.commit()

Top_User=pd.DataFrame(table6,columns=("States","Years","Quarter","Top_Dist","Top_Users"))

#Functions

def animate_all_amount(Map_User, Aggregated_Trans):
    ## Clone the geo data
    url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response = requests.get(url)
    data1 = json.loads(response.content)

    # Extract state names and sort them in alphabetical order
    state_names_tra = [feature["properties"]["ST_NM"] for feature in data1["features"]]
    state_names_tra.sort()

    # Create a DataFrame with the state names column
    df_state_names_tra = pd.DataFrame({"States": state_names_tra})

    frames = []

    for year in Map_User["Years"].unique():
        for quarter in Aggregated_Trans["Quarter"].unique():
            at1 = Aggregated_Trans[(Aggregated_Trans["Years"] == year) & (Aggregated_Trans["Quarter"] == quarter)]
            atf1 = at1[["States", "Trans_Amount"]]
            atf1 = atf1.sort_values(by="States")
            atf1["Years"] = year
            atf1["Quarter"] = quarter
            frames.append(atf1)

    merged_df = pd.concat(frames)

    fig_tra = px.choropleth(
        merged_df,
        geojson=data1,
        locations="States",
        featureidkey="properties.ST_NM",
        color="Trans_Amount",
        color_continuous_scale="Viridis",
        range_color=(0, 4000000000),
        hover_name="States",
        title="Transaction Amount Across States Over Time",
        animation_frame="Years",
        animation_group="Quarter"
    )

    fig_tra.update_geos(fitbounds="locations", visible=False)
    fig_tra.update_layout(width=600, height=700)
    fig_tra.update_layout(title_font={"size": 25})
    fig_tra.update_layout(coloraxis_colorbar=dict(title='Transaction Amount'))

    fig_tra.add_annotation(
        text="Important Information",
        x=0.5, y=-0.1,
        showarrow=False,
        font=dict(size=14, color="black"),
        bgcolor="white",
        bordercolor="black",
        borderwidth=1,
        opacity=0.8
    )

    # Optional: Adjust animation speed
    fig_tra.frames[0].update(layout_updatemenus=[
        dict(type="buttons", showactive=False, buttons=[
            dict(label="Play", method="animate", args=[None, dict(frame=dict(duration=1000, redraw=True), fromcurrent=True)])
        ])
    ])

    # Display the plotly chart using Streamlit
    st.plotly_chart(fig_tra)

# fetching transaction_type & count from aggre_trans 
    
def payment_count(Aggregated_Trans):
    attype = Aggregated_Trans[["Trans_Name", "Trans_Count"]]
    
    # Group the data by Transaction_type and calculate the sum of Transaction_count
    att1 = attype.groupby("Trans_Name")["Trans_Count"].sum().reset_index()

    fig_pc = px.bar(
        att1,
        x="Trans_Name",
        y="Trans_Count",
        title="Transaction Type and Transaction Count",
        color="Trans_Count",
        color_continuous_scale="Redor",
        labels={"Trans_Count": "Transaction Count"},
    )

    fig_pc.update_layout(
        width=800,
        height=500,
        xaxis_title="Transaction Type",
        yaxis_title="Transaction Count",
        title_font=dict(size=25),
        coloraxis_colorbar=dict(title='Transaction Count'),
    )

    # Display the plotly chart using Streamlit
    st.plotly_chart(fig_pc)



def animate_all_count(Aggregated_Trans):
    url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response = requests.get(url)
    data1 = json.loads(response.content)

    # Extract state names and sort them in alphabetical order
    state_names_tra = [feature["properties"]["ST_NM"] for feature in data1["features"]]
    state_names_tra.sort()

    # Create a DataFrame with the state names column
    df_state_names_tra = pd.DataFrame({"States": state_names_tra})

    frames = []

    for year in Aggregated_Trans["Years"].unique():
        for quarter in Aggregated_Trans["Quarter"].unique():
            at1 = Aggregated_Trans[(Aggregated_Trans["Years"] == year) & (Aggregated_Trans["Quarter"] == quarter)]
            atf1 = at1[["States", "Trans_Count"]]
            atf1 = atf1.sort_values(by="States")
            atf1["Years"] = year
            atf1["Quarter"] = quarter
            frames.append(atf1)

    merged_df = pd.concat(frames)

    fig_tra = px.choropleth(
        merged_df,
        geojson=data1,
        locations="States",
        featureidkey="properties.ST_NM",
        color="Trans_Count",
        color_continuous_scale="Viridis",  # Adjust color scale
        range_color=(0, 3000000),
        title="Transaction Count Across States Over Time",
        hover_name="States",
        animation_frame="Years",
        animation_group="Quarter"
    )

    fig_tra.update_geos(fitbounds="locations", visible=False)
    fig_tra.update_layout(width=800, height=700)
    fig_tra.update_layout(title_font={"size": 25})
    fig_tra.update_layout(coloraxis_colorbar=dict(title='Transaction Count'))

    # Display the plotly chart using Streamlit
    st.plotly_chart(fig_tra)

def payment_amount(Aggregated_Trans):
    attype = Aggregated_Trans[["Trans_Name", "Trans_Amount"]]
    
    # Group the data by Transaction_type and calculate the sum of Transaction_amount 
    att1 = attype.groupby("Trans_Name")["Trans_Amount"].sum().reset_index()
    att1_sorted = att1.sort_values(by="Trans_Amount", ascending=False)

    fig_tra_pa = px.bar(
        att1_sorted,
        x="Trans_Name",
        y="Trans_Amount",
        title="Transaction Type and Transaction Amount",
        color="Trans_Amount",
        color_continuous_scale="Blues",
        labels={"Trans_Amount": "Transaction Amount"},
    )

    fig_tra_pa.update_layout(
        width=800,
        height=600,
        xaxis_title="Transaction Type",
        yaxis_title="Transaction Amount",
        title_font=dict(size=25),
        coloraxis_colorbar=dict(title='Transaction Amount'),
    )

    # Display the plotly chart using Streamlit
    st.plotly_chart(fig_tra_pa)

def reg_all_states(Map_User, state):
    mu = Map_User[["States", "Map_Dist", "Map_Users"]]
    mu_state = mu[mu["States"] == state]

    # Group the data by Districts and calculate the sum of RegisteredUser
    mu_districts = mu_state.groupby("Map_Dist")["Map_Users"].sum().reset_index()

    fig_mu = px.bar(
        mu_districts,
        x="Map_Dist",
        y="Map_Users",
        title=f"Registered Users in {state} - District Wise",
        color="Map_Users",
        color_continuous_scale="Bluered",
        labels={"Map_Users": "Registered Users"},
    )

    fig_mu.update_layout(
        width=1000,
        height=500,
        xaxis_title="Districts",
        yaxis_title="Registered Users",
        title_font=dict(size=25),
        coloraxis_colorbar=dict(title='Registered Users'),
    )

    # Display the plotly chart using Streamlit
    st.plotly_chart(fig_mu)



def transaction_amount_year(Aggregated_Trans, selected_year):
    url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response = requests.get(url)
    data1 = json.loads(response.content)

    state_names_tra = [feature["properties"]['ST_NM'] for feature in data1["features"]]
    state_names_tra.sort()

    year = int(selected_year)
    atay = Aggregated_Trans[["States", "Years", "Trans_Amount"]]
    atay1 = atay.loc[(atay["Years"] == year)]

    # Group the data by States and calculate the sum of Transaction_amount
    atay2 = atay1.groupby("States")["Trans_Amount"].sum().reset_index()

    fig_atay = px.choropleth(
        atay2,
        geojson=data1,
        locations="States",
        featureidkey="properties.ST_NM",
        color="Trans_Amount",
        color_continuous_scale="rainbow",
        range_color=(0, 800000000000),
        title=f"Transaction Amount Across States - {year}",
        hover_name="States"
    )

    fig_atay.update_geos(fitbounds="locations", visible=False)
    fig_atay.update_layout(width=800, height=600)
    fig_atay.update_layout(title_font={"size": 25})
    fig_atay.update_layout(coloraxis_colorbar=dict(title='Transaction Amount'))

    # Display the plotly chart using Streamlit
    st.plotly_chart(fig_atay)


def payment_count_year(Aggregated_Trans, selected_year):
    year = int(selected_year)
    apc = Aggregated_Trans[["Trans_Name", "Years", "Trans_Count"]]
    apc1 = apc.loc[(apc["Years"] == year)]

    # Group the data by Transaction_type and calculate the sum of Transaction_count
    apc2 = apc1.groupby("Trans_Name")["Trans_Count"].sum().reset_index()

    fig_apc = px.bar(
        apc2,
        x="Trans_Name",
        y="Trans_Count",
        title=f"Payment Count by Type - {year}",
        color="Trans_Count",
        color_continuous_scale="Brwnyl",
        labels={"Trans_Count": "Payment Count"},
    )

    fig_apc.update_layout(
        width=800,
        height=600,
        xaxis_title="Payment Type",
        yaxis_title="Payment Count",
        title_font=dict(size=25),
        coloraxis_colorbar=dict(title='Payment Count'),
    )

    # Display the plotly chart using Streamlit
    st.plotly_chart(fig_apc)

def transaction_count_year(Aggregated_Trans, selected_year):
    url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response = requests.get(url)
    data1 = json.loads(response.content)
    state_names_tra = [feature["properties"]["ST_NM"] for feature in data1["features"]]
    state_names_tra.sort()

    year = int(selected_year)

    # Getting states & Transaction_count from aggr_trans
    atcy = Aggregated_Trans[["States", "Years", "Trans_Count"]]
    atcy1 = atcy.loc[atcy["Years"] == year]
    atcy2 = atcy1.groupby("States")["Trans_Count"].sum().reset_index()  # Calculating the total transaction_count

    fig_atcy = px.choropleth(
        atcy2,
        geojson=data1,
        locations="States",
        featureidkey="properties.ST_NM",
        color="Trans_Count",
        color_continuous_scale="rainbow",
        range_color=(0, 3000000000),
        title=f"Transaction Count Across States - {year}",
        hover_name="States"
    )

    fig_atcy.update_geos(fitbounds="locations", visible=False)
    fig_atcy.update_layout(width=800, height=700)
    fig_atcy.update_layout(title_font={"size": 25})
    fig_atcy.update_layout(coloraxis_colorbar=dict(title='Transaction Count'))

    # Display the plotly chart using Streamlit
    st.plotly_chart(fig_atcy)

def payment_amount_year(Aggregated_Trans, selected_year):
    year = int(selected_year)
    
    # Selecting data for the specified year
    apay = Aggregated_Trans[["Years", "Trans_Name", "Trans_Amount"]]
    apay_year = apay[apay["Years"] == year]
    
    # Group the data by Transaction_type and calculate the sum of Transaction_amount
    apay_grouped = apay_year.groupby("Trans_Name")["Trans_Amount"].sum().reset_index()

    fig_apay = px.bar(
        apay_grouped,
        x="Trans_Name",
        y="Trans_Amount",
        title=f"Payment Type and Payment Amount - {year}",
        color="Trans_Amount",
        color_continuous_scale="Burg",
        labels={"Trans_Amount": "Payment Amount"},
    )

    fig_apay.update_layout(
        width=800,
        height=600,
        xaxis_title="Payment Type",
        yaxis_title="Payment Amount",
        title_font=dict(size=25),
        coloraxis_colorbar=dict(title='Payment Amount'),
    )

    # Display the plotly chart using Streamlit
    st.plotly_chart(fig_apay)


def reg_state_all_RU(Map_User, selected_year, selected_state):
    year = int(selected_year)

    # Selecting data for the specified year and state
    mus = Map_User[["States", "Years", "Map_Dist", "Map_Users"]]
    mus_year_state = mus[(mus["States"] == selected_state) & (mus["Years"] == year)]

    # Group the data by Districts and calculate the sum of Registered Users
    mus_districts = mus_year_state.groupby("Map_Dist")["Map_Users"].sum().reset_index()

    fig_mus = px.bar(
        mus_districts,
        x="Map_Dist",
        y="Map_Users",
        title=f"Registered Users in {selected_state} - District Wise ({year})",
        color="Map_Users",
        color_continuous_scale="Cividis",
        labels={"Map_Users": "Registered Users"},
    )

    fig_mus.update_layout(
        width=800,
        height=600,
        xaxis_title="Districts",
        yaxis_title="Registered Users",
        title_font=dict(size=25),
        coloraxis_colorbar=dict(title='Registered Users'),
    )

    # Display the plotly chart using Streamlit
    st.plotly_chart(fig_mus)

def reg_state_all_TA(Map_Trans, selected_year, selected_state):
    year = int(selected_year)

    # Selecting data for the specified year and state
    mts = Map_Trans[["States", "Years", "Map_Dist", "Map_Amount"]]
    mts_year_state = mts[(mts["States"] == selected_state) & (mts["Years"] == year)]

    # Group the data by Districts and calculate the sum of Transaction Amount
    mts_districts = mts_year_state.groupby("Map_Dist")["Map_Amount"].sum().reset_index()

    fig_mts = px.bar(
        mts_districts,
        x="Map_Dist",
        y="Map_Amount",
        title=f"Transaction Amount in {selected_state} - District Wise ({year})",
        color="Map_Amount",
        color_continuous_scale="Darkmint",
        labels={"Map_Amount": "Transaction Amount"},
    )

    fig_mts.update_layout(
        width=800,
        height=600,
        xaxis_title="Districts",
        yaxis_title="Transaction Amount",
        title_font=dict(size=25),
        coloraxis_colorbar=dict(title='Transaction Amount'),
    )

    # Display the plotly chart using Streamlit
    st.plotly_chart(fig_mts)

#------------- Query-----------#

def ques1():
    brand= Aggregated_User[["User_Name","User_Count"]]
    brand1= brand.groupby("User_Name")["User_Count"].sum().sort_values(ascending=False)
    brand2= pd.DataFrame(brand1).reset_index()

    fig_brands= px.pie(brand2, values= "User_Count", names= "User_Name", color_discrete_sequence=px.colors.sequential.dense_r,
                       title= "Top Mobile Brands of Transaction_count")
    return st.plotly_chart(fig_brands)

def ques2():
    lt= Aggregated_Trans[["States", "Trans_Amount"]]
    lt1= lt.groupby("States")["Trans_Amount"].sum().sort_values(ascending= True)
    lt2= pd.DataFrame(lt1).reset_index().head(10)

    fig_lts= px.bar(lt2, x= "States", y= "Trans_Amount",title= "LOWEST TRANSACTION AMOUNT and STATES",
    color_discrete_sequence= px.colors.sequential.Oranges_r)
    return st.plotly_chart(fig_lts)

def ques3():
    htd= Map_Trans[["Map_Dist", "Map_Amount"]]
    htd1= htd.groupby("Map_Dist")["Map_Amount"].sum().sort_values(ascending=False)
    htd2= pd.DataFrame(htd1).head(10).reset_index()

    fig_htd= px.pie(htd2, values= "Map_Amount", names= "Map_Dist", title="TOP 10 DISTRICTS OF HIGHEST TRANSACTION AMOUNT",
                    color_discrete_sequence=px.colors.sequential.Emrld_r)
    return st.plotly_chart(fig_htd)

def ques4():
    htd= Map_Trans[["Map_Dist", "Map_Amount"]]
    htd1= htd.groupby("Map_Dist")["Map_Amount"].sum().sort_values(ascending=True)
    htd2= pd.DataFrame(htd1).head(10).reset_index()

    fig_htd= px.pie(htd2, values= "Map_Amount", names= "Map_Dist", title="TOP 10 DISTRICTS OF LOWEST TRANSACTION AMOUNT",
                    color_discrete_sequence=px.colors.sequential.Greens_r)
    return st.plotly_chart(fig_htd)

def ques5():
    sa= Map_User[["States", "Map_Appopen"]]
    sa1= sa.groupby("States")["Map_Appopen"].sum().sort_values(ascending=False)
    sa2= pd.DataFrame(sa1).reset_index().head(10)

    fig_sa= px.bar(sa2, x= "States", y= "Map_Appopen", title="Top 10 States With AppOpens",
                color_discrete_sequence= px.colors.sequential.deep_r)
    return st.plotly_chart(fig_sa)

def ques6():
    sa= Map_User[["States", "Map_Appopen"]]
    sa1= sa.groupby("States")["Map_Appopen"].sum().sort_values(ascending=True)
    sa2= pd.DataFrame(sa1).reset_index().head(10)

    fig_sa= px.bar(sa2, x= "States", y= "Map_Appopen", title="lowest 10 States With AppOpens",
                color_discrete_sequence= px.colors.sequential.dense_r)
    return st.plotly_chart(fig_sa)

def ques7():
    stc= Aggregated_Trans[["States", "Trans_Count"]]
    stc1= stc.groupby("States")["Trans_Count"].sum().sort_values(ascending=True)
    stc2= pd.DataFrame(stc1).reset_index()

    fig_stc= px.bar(stc2, x= "States", y= "Trans_Count", title= "STATES WITH LOWEST TRANSACTION COUNT",
                    color_discrete_sequence= px.colors.sequential.Jet_r)
    return st.plotly_chart(fig_stc)

def ques8():
    stc= Aggregated_Trans[["States", "Trans_Count"]]
    stc1= stc.groupby("States")["Trans_Count"].sum().sort_values(ascending=False)
    stc2= pd.DataFrame(stc1).reset_index()

    fig_stc= px.bar(stc2, x= "States", y= "Trans_Count", title= "STATES WITH HIGHEST TRANSACTION COUNT",
                    color_discrete_sequence= px.colors.sequential.Magenta_r)
    return st.plotly_chart(fig_stc)

def ques9():
    ht= Aggregated_Trans[["States", "Trans_Amount"]]
    ht1= ht.groupby("States")["Trans_Amount"].sum().sort_values(ascending= False)
    ht2= pd.DataFrame(ht1).reset_index().head(10)

    fig_lts= px.bar(ht2, x= "States", y= "Trans_Amount",title= "HIGHEST TRANSACTION AMOUNT and STATES",
                    color_discrete_sequence= px.colors.sequential.Oranges_r)
    return st.plotly_chart(fig_lts)

def ques10():
    dt= Map_Trans[["Map_Dist", "Map_Amount"]]
    dt1= dt.groupby("Map_Dist")["Map_Amount"].sum().sort_values(ascending=True)
    dt2= pd.DataFrame(dt1).reset_index().head(50)

    fig_dt= px.bar(dt2, x= "Map_Dist", y= "Map_Amount", title= "DISTRICTS WITH LOWEST TRANSACTION AMOUNT",
                color_discrete_sequence= px.colors.sequential.Mint_r)
    return st.plotly_chart(fig_dt)

####Streamlit Part

st.set_page_config(page_title="Phonepe",
                    layout="wide")
selected = option_menu(None,
                      options = ["About","Home","Analysis","Insights"],
                      icons = ["bar-chart","house","toggles","at"],                        
                      default_index=0,
                        orientation="horizontal",
                        styles={"container": {"width": "100%"},
                                "icon": {"color": "white", "font-size": "24px"},
                                 "nav-link": {"font-size": "24px", "text-align": "center", "margin": "-4px" ,"--hover-color": "#800080"},
                                "nav-link-selected": {"background-color": "#800080"},
                                "nav": {"background-color": "#E6E6FA"}})

# ABOUT PAGE
if selected == "About":
    col1, col2 = st.columns(2)
    col1.image("https://tse3.mm.bing.net/th?id=OIP.eCSo2z86EagDx42Ie9-9RQHaDt&pid=Api&P=0&h=180", width=500)

    with col1:
        st.subheader(
            "PhonePe  is an Indian digital payments and financial technology company headquartered in Bengaluru, Karnataka, India. PhonePe was founded in December 2015, by Sameer Nigam, Rahul Chari and Burzin Engineer. The PhonePe app, based on the Unified Payments Interface (UPI), went live in August 2016. It is owned by Flipkart, a subsidiary of Walmart.")
        st.markdown("[Download App](https://www.phonepe.com/app-download/)")

    with col2:
        st.image("https://www.techgenyz.com/wp-content/uploads/2021/09/PhonePe.jpg")
    
    st.write("----")

# HOME PAGE 
if selected == "Home":
    col1,col2 = st.columns(2)
    with col1:
        st.video("https://youtu.be/c_1H6vivsiA")
    
    with col2:
        st.title(':violet[PHONEPE PULSE DATA VISUALISATION]')
        st.subheader(':violet[Phonepe Pulse]:')
        st.write('PhonePe Pulse is a feature offered by the Indian digital payments platform called PhonePe.PhonePe Pulse provides users with insights and trends related to their digital transactions and usage patterns on the PhonePe app.')
        st.subheader(':violet[Phonepe Pulse Data Visualisation]:')
        st.write('Data visualization refers to the graphical representation of data using charts, graphs, and other visual elements to facilitate understanding and analysis in a visually appealing manner.'
                 'The goal is to extract this data and process it to obtain insights and information that can be visualized in a user-friendly manner.')

    st.write("----")

#ANALYSIS PAGE 
if selected == "Analysis":
    # Import your visualization functions here (animate_all_amount, payment_count, etc.)
    selected_state = None  # Declare selected_state globally
    
    def main():

        global selected_state  # Make selected_state a global variable
        st.subheader('Analysis done on the basis of All India, States, Districts, and Top categories between 2018 and 2023')

        selected_year = st.selectbox("Select the Year", ("All", "2018", "2019", "2020", "2021", "2022", "2023"))

        if selected_year == "All":
            show_all_analysis()
        else:
            show_yearly_analysis(selected_year)

    def show_all_analysis():
        col1, col2 = st.columns(2)

        with col1:
            animate_all_amount(Map_User, Aggregated_Trans)  # Pass required parameters
            payment_count(Aggregated_Trans)

        with col2:
            animate_all_count(Aggregated_Trans)
            payment_amount(Aggregated_Trans)

        global selected_state  # Use the global selected_state
        selected_state = st.selectbox("Select the State", get_state_names())
        reg_all_states(Map_User,selected_state)

    def show_yearly_analysis(selected_year):
        col1, col2 = st.columns(2)

        with col1:
            transaction_amount_year(Aggregated_Trans, selected_year)
            payment_count_year(Aggregated_Trans, selected_year)

        with col2:
            transaction_count_year(Aggregated_Trans, selected_year)
            payment_amount_year(Aggregated_Trans, selected_year)

            global selected_state  # Use the global selected_state
            selected_state = st.selectbox("Select the State", get_state_names())
            reg_state_all_RU(selected_year)
            reg_state_all_TA(selected_year)


    def get_state_names():
        return ['Andaman & Nicobar', 'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chandigarh', 'Chhattisgarh',
                'Dadra and Nagar Haveli and Daman and Diu', 'Delhi', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh',
                'Jammu & Kashmir', 'Jharkhand', 'Karnataka', 'Kerala', 'Ladakh', 'Lakshadweep', 'Madhya Pradesh',
                'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Puducherry', 'Punjab', 'Rajasthan',
                'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal']

    if __name__ == "__main__":
        main()

#INSIGHTS PAGE
if selected == "Insights":

    ques= st.selectbox("select the question",('Top Brands Of Mobiles Used','States With Lowest Trasaction Amount',
                                  'Districts With Highest Transaction Amount','Top 10 Districts With Lowest Transaction Amount',
                                  'Top 10 States With AppOpens','Least 10 States With AppOpens','States With Lowest Trasaction Count',
                                 'States With Highest Trasaction Count','States With Highest Trasaction Amount',
                                 'Top 50 Districts With Lowest Transaction Amount'))
    if ques=="Top Brands Of Mobiles Used":
        ques1()

    elif ques=="States With Lowest Trasaction Amount":
        ques2()

    elif ques=="Districts With Highest Transaction Amount":
        ques3()

    elif ques=="Top 10 Districts With Lowest Transaction Amount":
        ques4()

    elif ques=="Top 10 States With AppOpens":
        ques5()

    elif ques=="Least 10 States With AppOpens":
        ques6()

    elif ques=="States With Lowest Trasaction Count":
        ques7()

    elif ques=="States With Highest Trasaction Count":
        ques8()

    elif ques=="States With Highest Trasaction Amount":
        ques9()

    elif ques=="Top 50 Districts With Lowest Transaction Amount":
        ques10()

   



























# st.set_page_config(page_title="Phonepe",
#                     layout="wide")
# selected = option_menu(None,
#                        options = ["About","Home","Analysis","Insights"],
#                        icons = ["bar-chart","house","toggles","at"],
#                        default_index=0,
#                        orientation="horizontal",
#                        styles={"container": {"width": "100%"},
#                                 "icon": {"color": "white", "font-size": "24px"},
#                                 "nav-link": {"font-size": "24px", "text-align": "center", "margin": "-4px" ,"--hover-color": "#800080"},
#                                 "nav-link-selected": {"background-color": "#800080"},
#                                 "nav": {"background-color": "#E6E6FA"}})

# # ABOUT PAGE
# if selected == "About":
#     col1, col2 = st.columns(2)
#     col1.image("https://tse3.mm.bing.net/th?id=OIP.eCSo2z86EagDx42Ie9-9RQHaDt&pid=Api&P=0&h=180", width=500)
    
#     with col1:
#         st.subheader(
#             "PhonePe  is an Indian digital payments and financial technology company headquartered in Bengaluru, Karnataka, India. PhonePe was founded in December 2015, by Sameer Nigam, Rahul Chari and Burzin Engineer. The PhonePe app, based on the Unified Payments Interface (UPI), went live in August 2016. It is owned by Flipkart, a subsidiary of Walmart.")
#         st.markdown("[Download App](https://www.phonepe.com/app-download/)")

#     with col2:
#         st.image("https://www.techgenyz.com/wp-content/uploads/2021/09/PhonePe.jpg")
    
#     st.write("----")

# # HOME PAGE
# if selected == "Home":
#     col1,col2 = st.columns(2)
#     with col1:
#         st.video("https://youtu.be/c_1H6vivsiA")
    
#     with col2:
#         st.title(':violet[PHONEPE PULSE DATA VISUALISATION]')
#         st.subheader(':violet[Phonepe Pulse]:')
#         st.write('PhonePe Pulse is a feature offered by the Indian digital payments platform called PhonePe.PhonePe Pulse provides users with insights and trends related to their digital transactions and usage patterns on the PhonePe app.')
#         st.subheader(':violet[Phonepe Pulse Data Visualisation]:')
#         st.write('Data visualization refers to the graphical representation of data using charts, graphs, and other visual elements to facilitate understanding and analysis in a visually appealing manner.'
#                  'The goal is to extract this data and process it to obtain insights and information that can be visualized in a user-friendly manner.')

#     st.write("----")

# # ANALYSIS PAGE
# if selected == "Analysis":
#     st.title(':violet[ANALYSIS]')
#     st.subheader('Analysis done on the basis of All India ,States, Districts and Top categories between 2018 and 2023')
#     select = option_menu(None,
#                          options=["INDIA", "STATES", "TOP CATEGORIES" ],
#                          default_index=0,
#                          orientation="horizontal",
#                          styles={"container": {"width": "100%"},
#                                    "nav-link": {"font-size": "20px", "text-align": "center", "margin": "-2px"},
#                                    "nav-link-selected": {"background-color": "#6F36AD"}})
    
#     if select == "INDIA":
#         tab1, tab2 = st.tabs(["TRANSACTION","USER"])

#          # TRANSACTION TAB
#         with tab1:
#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 year = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='year')
#             with col2:
#                 qtr = st.selectbox('**Select Quarter**', ('1', '2', '3', '4'), key='qtr')
#             with col3:
#                 tran_type = st.selectbox('**Select Transaction type**',
#                                             ('Recharge & bill payments', 'Peer-to-peer payments',
#                                              'Merchant payments', 'Financial Services', 'Others'), key='tran_type')
                

