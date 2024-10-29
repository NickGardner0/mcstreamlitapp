import pandas as pd
import numpy as np
import random as rnd
import pickle as pkle
import os.path
import streamlit as st
import plotly.express as px
import plotly.colors as pcolors

def gen_number():
    st.session_state["ran"] = rnd.randint(1,10000)
    return

st.set_page_config(page_title="Monte Carlo Pi", page_icon=':m:',layout="wide")

if "intro" not in st.session_state:
    st.session_state["intro"] = False

if "ran" not in st.session_state:
    st.session_state["ran"] = rnd.randint(1,10000)

# start with an explination of why MC
col1,col2,col3 = st.columns([1,2,1])

with col2:
    st.title("Using Monte Carlo to Estimate π values ")
    st.write("""Monte Carlo simulations (MCS) are a class of computational algorithms that rely \
             on random sampling to solve complex mathematical and probabilistic problems. \
             They are especially useful when dealing with systems that have a high degree of \
             uncertainty, non-linearity, or many interdependent variables. 
             
             These algorithms have application across many fields, but are most useful in: """)

# create 2 columns so we can add text on one side and a gif on the other
# Space out the maps so the first one is 2x the size of the second
col1, col2,col3,col4 = st.columns((1,1,1,1))
#column 1
with col2:
    st.write(""" 
**Risk Analysis and Uncertainty:** MCS helps model the range of possible outcomes in uncertain situations by running multiple iterations with different sets of random inputs. \
             It provides probability distributions for outcomes instead of single-point estimates.


**Optimization Problems:** Monte Carlo methods are used to find the best solution among many possibilities, \
             especially in high-dimensional optimization where deterministic approaches are impractical. 


**Probability Calculations:** In cases where it is difficult to compute exact probabilities analytically, such as in finance or physics, \
             Monte Carlo simulations can estimate probabilities through repeated random sampling.

**Model Validation and Forecasting:** MCS is used to validate complex models by simulating various inputs and comparing the predicted outcomes against real-world data. \
      It is also used for forecasting future states under uncertain conditions. """)
    


# column 3: multiple GIFs with alignment and reduced spacing
with col3:
    # Move the first GIF slightly to the right
    st.markdown("<div style='text-align: center; margin-left: 30px; margin-bottom: -10px;'>", unsafe_allow_html=True)
    st.image('MC_pi/brownian2_motion.gif', caption='Stochastic', width=300)
    st.markdown("</div>", unsafe_allow_html=True)

    # Keep the second GIF in the same spot
    st.markdown("<div style='text-align: center; margin-top: -20px;'>", unsafe_allow_html=True)
    st.image('MC_pi/Pi_30K.gif', caption='π-variance', width=370)
    st.markdown("</div>", unsafe_allow_html=True)






with col2:
    st.subheader("*Lets run some sims*")

    if st.button("Open simulation", key='start_'):
        st.session_state.intro = True

if st.session_state['intro']:

    st.write("---")

    ### Create sidebar
    with st.sidebar:

        st.title("Parameters")
        st.markdown("Select the total number of randomly generated \
        points you want to use to estimate π values:")
        iterations = st.number_input("Total Number of Points:", min_value=1,max_value= 10000, value=st.session_state["ran"])
        st.button("Random number", on_click=gen_number)

    col1,col2 = st.columns(2)

    with col1:
        # section 2 running a MC simulation
        st.header('Run a simple MC algorithm')
        st.write("""
Enter a value in the sidebar to set the total number of points used to estimate π \

This simulation leverages the ratio of the areas: the fraction of randomly placed points falling inside a unit circle (radius = 1) relative to those inside the enclosing square (side length = 2) \
converges to π. This relationship is the foundation for using Monte Carlo methods to approximate π efficiently. \
The plot visualizes the random points with a circle and square overlay, illustrating the probabilistic nature of the estimation. """)


    # use the total number of points to generate pairs of x and y points for our graph
    x_list = []
    y_list = []
    inside_count = 0
    iterations = int(iterations)
    for num in range(iterations):
        # get the random values for the y and y coordinates, we want them to be generated
        # between -1 and 1 for both values to fit in our square
        x_random = rnd.uniform(-1,1)
        x_list.append(x_random)
        y_random = rnd.uniform(-1,1)
        y_list.append(y_random)

        #check if the point is inside the circle
        if (x_random**2 +y_random**2) <= 1.0:
            inside_count += 1

    fig2 = px.scatter(
            x=x_list,
            y=y_list)
            #size=1)
    fig2.update_layout(width=700,
    height=700)
    fig2.add_shape(
        type="circle",
        x0=-1, x1=1,
        y0=-1, y1=1,
        line_color="red")

    # sent plot to streamlit
    col2.plotly_chart(fig2)

    # finally lets display our estimation of Pi, the true value and the percent
    # difference between the two (in this example r = 1, so dont need to divide by it)
    estimated_pi = 4*inside_count/iterations

    #calculate the percent difference from the standard: |value - true_value|/|true_value|*100%
    diff_percent = abs(estimated_pi-np.pi)/np.pi*100

    with st.sidebar:
        st.write("Number of points:",iterations)
        st.write("Your Estimation of Pi:", estimated_pi)
        st.write("True Value of Pi:", np.pi)
        st.write("The percent error between your estimation and the true value is:", round(diff_percent,3), "%")

    st.write("---")
    # lets track how the estimations change as we change the number of iterations!
    # actually going to add a new point to the graph for every new estimation of \pi
    col3, col4 = st.columns(2)
    with col3:
        st.header("Impact of Point Count on π Estimation")
        st.write("""
As the number of points in a Monte Carlo simulation increases, the Pi estimate becomes more accurate. \
This behavior is explained by the Law of Large Numbers, which states that as the sample size grows, the average of results converges to the expected value. \
The graph illustrates this convergence: early estimates vary widely, especially with small sample sizes (e.g., 10 or 100 points). \
As the number of points increases, the spread of values narrows, stabilizing around the true value of π (marked by the red line). With large point counts (1,000 or more), individual variations become negligible. """) 


        x_log = st.checkbox("log Number of Points", key="graph_1")

    #calculate error to store in data
    error = abs(estimated_pi-np.pi)/np.pi*100

    # check if a pickled file with all the previous dat is there, if not create Data
    # this will check for and create a new pkl file in main directory on streamlit servers
    data_file = os.path.isfile('pkled_data.pkl')

    if data_file:
        #the file exists, we want to read in previous data
        converge = pd.read_pickle('pkled_data.pkl')
        ## leave os remove file here until change to database structure
        #os.remove('pkled_data.pkl')
    else:
        #create database to work with
        converge = pd.DataFrame([[iterations, estimated_pi, error]], columns=['N_points','pi_est',"error"])

    if converge.iloc[-1,1] != estimated_pi:
        # add a line with new data in the converge
        converge.loc[len(converge)] = [iterations,estimated_pi,error]

#plot the convergence
    fig2 = px.scatter(
            x=converge['N_points'],
            y=converge['pi_est'],
            log_x=x_log,
            labels={'x':"Number of Points Used in Estimation",'y':"Calculated Pi values"})
            #size=1)

    fig2.add_shape(
        type="line",
        x0=1, x1=10000,
        y0=np.pi, y1=np.pi,
        line_color="red")

#send figure to streamlit
    col4.plotly_chart(fig2)

    st.write("---")
    # section on the 3rd grph that sorts points based on their order

    col5,col6 = st.columns(2)

    with col5:
        st.header('Tracking Progress of π Estimates')
        st.write("""
This graph plots each new π estimate based on the number of points used in each trial.\
 The color of each point corresponds to the total points used, highlighting how higher point counts yield estimates closer to π. \
As point counts increase by orders of magnitude (e.g., 1–9 vs. 5000 points), the spread of estimates decreases. \
Lower point counts show greater variability, while larger samples converge near the true value of π (shown by the red line). """) 


        color = st.radio("Color points by:", ["Number of Points", "% Error"])
        range = st.slider("Range of Pi values:",0.0,4.0,[0.0,4.0],0.5)
        range = [range[0]-0.25, range[1]+0.25]

        if color == "Number of Points":
            column = "N_points"
        else:
            column = "error"
    fig2 = px.scatter(
            x=converge.index,
            y=converge['pi_est'],
            color=converge[column],
            color_continuous_scale = px.colors.sequential.Sunsetdark,
            labels={'x':"Trial Number",'y':"Calculated Pi values", 'color':"# of Points"})
            #size=1)
    fig2.update_layout(yaxis=dict(range=range))
    fig2.add_shape(
        type="line",
        x0=0, x1=len(converge),
        y0=np.pi, y1=np.pi,
        line_color="red")

    col6.plotly_chart(fig2)

    st.write("---")
    # add in graph on how the % errors change as iterations are increased!

    col7,col8 = st.columns(2)

    with col7:
        st.header('% Error Across Iterations')

        st.write("""
This plot shows how % error decreases as the number of points used increases. At low point counts (e.g., <5 points), \
the error can reach 100%, but it quickly drops to just a few percent with around 100 points. \
To analyze the error distribution more effectively, you can apply a logarithmic scale to the axes. \
This highlights the order of magnitude changes in both % error and point count, making trends more visible at different scales. """) 


        # add checkboxes to sidebar to make the axes log!
    
        x_log = st.checkbox("log Number of Points")
        y_log = st.checkbox("log % Error")

    fig2 = px.scatter(
            x=converge['N_points'],
            y=converge['error'],
            color=converge['N_points'],
            color_continuous_scale = px.colors.sequential.Sunsetdark,
            log_y=y_log, log_x=x_log,
            labels={'x':"Number of Points Used in Estimation",'y':"% Error",'color':"# of Points"})
            #size=1)
    col8.plotly_chart(fig2)

    #repickle file with added data
    converge.to_pickle('pkled_data.pkl')
