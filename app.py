import html
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from rescue_engine import allocate, explain

st.set_page_config(page_title='FoodClock | Rescue Operations',page_icon='◷',layout='wide',initial_sidebar_state='collapsed')
st.markdown('''<style>
[data-testid="stHeader"]{background:transparent} .block-container{max-width:1440px;padding-top:2rem;padding-bottom:2rem} h1,h2,h3{letter-spacing:-.035em} [data-testid="stMetric"]{background:white;border:1px solid #dce6e0;border-radius:14px;padding:16px 20px;box-shadow:0 3px 12px #153b2810} [data-testid="stMetricValue"]{font-size:2.15rem;font-weight:700} [data-testid="stMetricLabel"]{color:#52685e} div[data-testid="stVerticalBlockBorderWrapper"]{background:white;border-radius:14px;border-color:#dce6e0} .mast{background:#113e32;color:#fff;border-radius:18px;padding:24px 30px;display:flex;align-items:center;justify-content:space-between;gap:18px;flex-wrap:wrap}.brand{font-size:28px;font-weight:800;letter-spacing:-1.5px}.brand small{font-size:12px;letter-spacing:2px;color:#a5d9c6;display:block;font-weight:600}.mast p{color:#d1e5dc;margin:8px 0 0;font-size:14px}.tag{border:1px solid #598578;border-radius:30px;padding:8px 13px;font-size:12px;color:#d4f1e5}.eyebrow{font-size:11px;text-transform:uppercase;letter-spacing:2px;color:#087f60;font-weight:700;margin-top:12px}.clock{border:1px solid #e3eae5;border-radius:12px;padding:12px;margin-bottom:10px;background:#fff}.clocktop{display:flex;justify-content:space-between;gap:8px;align-items:center}.track{height:6px;background:#e8eeea;border-radius:8px;margin-top:10px;overflow:hidden}.track span{display:block;height:6px;border-radius:8px}.sub{font-size:12px;color:#60746a}.big{font-size:22px;font-weight:800}.stButton button,.stDownloadButton button{border-radius:8px;font-weight:600} [data-testid="stRadio"] label{font-weight:600} @media(max-width:600px){.mast{padding:18px}.brand{font-size:24px}}
</style>''',unsafe_allow_html=True)

def demo():
    return ([dict(name='Campus vegetable meals',meals=80,minutes=40,x=0.,y=0.,storage='Hot-held',verified=True),dict(name='Wedding hall meals',meals=120,minutes=40,x=4.,y=0.,storage='Hot-held',verified=True),dict(name='Bakery bread',meals=70,minutes=240,x=2.,y=3.,storage='Ambient',verified=True)], [dict(name='Community kitchen A',demand=100,capacity=100,x=1.,y=0.,storage='Hot-held',active=True),dict(name='Shelter B',demand=100,capacity=100,x=-5.,y=0.,storage='Hot-held',active=True),dict(name='Food bank C',demand=70,capacity=70,x=2.,y=4.,storage='Ambient',active=True)])
if 'batches' not in st.session_state: st.session_state.batches,st.session_state.recipients=demo()
st.markdown('<div class="mast"><div><div class="brand">◷ FoodClock<small>RESCUE OPERATIONS</small></div><p>Every minute. Every meal. Matters.</p></div><div class="tag">SIMULATION / STUDENT PROTOTYPE</div></div>',unsafe_allow_html=True)
page=st.radio('Workspace',['Overview','Donations','Recipients','Scenario lab','Methodology'],horizontal=True,label_visibility='collapsed')
B=st.session_state.batches; R=st.session_state.recipients

def plot_layout(fig,height=350):
    fig.update_layout(height=height,margin=dict(l=15,r=15,t=25,b=20),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#30483d',size=12),legend=dict(orientation='h',y=-.18))
    fig.update_xaxes(gridcolor='#e4ece7'); fig.update_yaxes(gridcolor='#e4ece7'); return fig

def network(bs,rs,plan):
    fig=go.Figure()
    for p in plan:
        b=next(b for b in bs if b['name']==p['batch']); r=next(r for r in rs if r['name']==p['recipient'])
        fig.add_trace(go.Scatter(x=[b['x'],r['x']],y=[b['y'],r['y']],mode='lines',line=dict(width=2+p['meals']/35,color='#38a789'),hovertemplate=f"{html.escape(p['batch'])} → {html.escape(p['recipient'])}<br>{p['meals']} meals<extra></extra>",showlegend=False))
    for items,label,symbol,color in [(bs,'Donations','square','#db9b36'),(rs,'Recipients','circle','#087f60')]:
        fig.add_trace(go.Scatter(x=[a['x'] for a in items],y=[a['y'] for a in items],text=[a['name'] for a in items],mode='markers+text',textposition='top center',marker=dict(size=13,symbol=symbol,color=color,line=dict(width=2,color='white')),name=label))
    fig.update_xaxes(title='Grid X (km)');fig.update_yaxes(title='Grid Y (km)',scaleanchor='x',scaleratio=1)
    return plot_layout(fig,390)

def clocks(bs):
    for b in sorted(bs,key=lambda b:b['minutes']):
        m=max(0,b['minutes']); c='#b93838' if m<=30 else '#a96514' if m<=60 else '#087f60'; pct=min(100,m/240*100)
        st.markdown(f'<div class="clock"><div class="clocktop"><div><b>{html.escape(b["name"])}</b><div class="sub">{b["meals"]} meals · {html.escape(b["storage"])}</div></div><div class="big" style="color:{c}">{m}m</div></div><div class="track"><span style="width:{pct}%;background:{c}"></span></div></div>',unsafe_allow_html=True)
    if not bs: st.info('No donations listed.')

def show_plan(bs,rs,delay,elapsed,buffer,disabled):
    bs=[dict(b,minutes=b['minutes']-elapsed) for b in bs];rs=[dict(r,active=r['active'] and r['name'] not in disabled) for r in rs]
    plan=allocate(bs,rs,delay,buffer);baseline=allocate(bs,rs,delay,buffer,False)
    total=sum(b['meals'] for b in bs);saved=sum(p['meals'] for p in plan);base=sum(p['meals'] for p in baseline)
    for col,label,value in zip(st.columns(4),['Listed meals','Optimized allocation','Unallocated meals','Urgent batches'],[total,saved,total-saved,sum(0<b['minutes']<=60 for b in bs)]): col.metric(label,value)
    l,r=st.columns([1.65,1])
    with l:
        with st.container(border=True):
            st.subheader('Rescue network');st.caption('Illustrative coordinates · line width represents allocated meals');st.plotly_chart(network(bs,rs,plan),use_container_width=True,config={'displayModeBar':False})
    with r:
        with st.container(border=True):
            st.subheader('Deadline monitor');st.caption('Simulated minutes remaining');clocks(bs)
    l,r=st.columns([1.65,1])
    with l:
        with st.container(border=True):
            st.subheader('Dispatch recommendations');st.caption('Planning only — no actual dispatch')
            if plan:
                df=pd.DataFrame(plan);st.dataframe(df.rename(columns={'batch':'Food batch','recipient':'Destination','meals':'Meals','travel_minutes':'Trip (min)','latest_start_in_minutes':'Latest start (min)','storage':'Handling'}),hide_index=True,use_container_width=True);st.download_button('Export rescue plan',df.to_csv(index=False),'rescue_plan.csv','text/csv')
            else: st.info('No feasible matches in this scenario.')
    with r:
        with st.container(border=True):
            st.subheader('Optimization advantage');st.metric('Additional allocated meals',saved-base);fig=go.Figure(go.Bar(x=[base,saved],y=['Nearest first','FoodClock'],orientation='h',marker_color=['#a9bcb2','#087f60'],text=[base,saved],textposition='auto'));fig.update_xaxes(range=[0,max(total,1)*1.12]);st.plotly_chart(plot_layout(fig,210),use_container_width=True,config={'displayModeBar':False})
    with st.container(border=True):
        st.subheader('Allocation exceptions');reasons=explain(bs,rs,plan,delay,buffer)
        if reasons:st.dataframe(pd.DataFrame(reasons),hide_index=True,use_container_width=True)
        else:st.success('All listed meals have a feasible allocation.')
    st.caption('Fictional data. Trip estimates: 3 min/km + 10 min handling + simulated delay. A feasible schedule does not establish food safety.')

if page in ['Overview','Scenario lab']:
    st.markdown('<div class="eyebrow">Operations / '+('Performance' if page=='Overview' else 'Stress testing')+'</div>',unsafe_allow_html=True)
    st.title('Rescue command center' if page=='Overview' else 'Disruption scenario lab')
    delay=0;elapsed=0;disabled=[]
    with st.expander('Planning controls',expanded=page=='Scenario lab'):
        buffer=st.slider('Planning buffer (minutes)',5,60,15)
        if page=='Scenario lab':
            a,b=st.columns(2);delay=a.slider('Transportation delay (minutes)',0,180,30);elapsed=b.slider('Time elapsed (minutes)',0,240,0);disabled=st.multiselect('Unavailable recipients',[r['name'] for r in R]);before=sum(p['meals'] for p in allocate(B,R,0,buffer));st.caption(f'Before disruption: {before} planned meals.')
    show_plan(B,R,delay,elapsed,buffer,disabled)
elif page in ['Donations','Recipients']:
    donation=page=='Donations';items=B if donation else R
    st.title('Donation inventory' if donation else 'Recipient directory')
    l,r=st.columns([1,1.4])
    with l:
        with st.container(border=True):
            st.subheader('Register '+('food batch' if donation else 'recipient'))
            with st.form('register'):
                name=st.text_input('Food batch name' if donation else 'Organization name');qty=st.number_input('Available meals' if donation else 'Meals required',1,10000,50);other=st.number_input('Declared distribution window (min)' if donation else 'Receiving capacity',1,1440 if donation else 10000,90 if donation else 50)
                a,b=st.columns(2);x=a.number_input('Grid X (km)',-100.,100.,0.);y=b.number_input('Grid Y (km)',-100.,100.,0.);storage=st.selectbox('Handling type',['Hot-held','Chilled','Ambient']);flag=st.checkbox('Handling and deadline confirmed (simulated)' if donation else 'Available to receive',value=not donation)
                if st.form_submit_button('Save record',type='primary',use_container_width=True):
                    if not name.strip() or any(i['name'].casefold()==name.strip().casefold() for i in items):st.error('Enter a unique nonempty name.')
                    else:
                        items.append(dict(name=name.strip(),x=x,y=y,storage=storage,**(dict(meals=qty,minutes=other,verified=flag) if donation else dict(demand=qty,capacity=other,active=flag))));st.success('Record saved for this session.')
    with r:
        with st.container(border=True):
            st.subheader('Current records');st.dataframe(pd.DataFrame(items),hide_index=True,use_container_width=True)
            if items:
                selected=st.selectbox('Select record to remove',[i['name'] for i in items]);confirm=st.checkbox('Confirm removal')
                if st.button('Remove record',disabled=not confirm):
                    st.session_state['batches' if donation else 'recipients']=[i for i in items if i['name']!=selected];st.rerun()
else:
    st.title('How FoodClock works');st.write('The integer linear programming engine maximizes allocated meals subject to donation supply, recipient demand and capacity, handling compatibility and estimated deadlines. A second optimization favors urgent batches and shorter trips. The baseline is greedy nearest-first matching.');st.code('Latest start = remaining window − trip duration − planning buffer',language=None);st.info('Prototype only: fictional data, session storage, no live traffic, no food safety certification. AI assistance: ChatGPT contributed to code and documentation.')
    if st.button('Reset fictional demonstration records'):st.session_state.batches,st.session_state.recipients=demo();st.rerun()
