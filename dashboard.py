import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import webbrowser
from threading import Thread
import time

def run_statistics_dashboard(session):
    """
    Запускает дашборд статистики в браузере
    
    Args:
        session: SQLAlchemy сессия для доступа к данным
    """
    print("Запуск дашборда статистики...")
    
    # Создаем Dash
    app = dash.Dash(__name__, title="Статистика салона красоты")
    
    def get_statistics_data():
        from models.schedule import Appointment
        from models.services import Service
        from models.masters import Master
        from models.clients import Client
        
        print("Загрузка данных из базы...")
        
        try:
            appointments = (session.query(
                Appointment,
                Service.service_name,
                Master.first_name,
                Master.last_name,
                Client.first_name.label('client_first_name'),
                Client.last_name.label('client_last_name')
            )
            .join(Service, Appointment.service_id == Service.service_id)
            .join(Master, Appointment.master_id == Master.master_id)
            .join(Client, Appointment.client_id == Client.client_id)
            .all())
            
            data = []
            for app, service_name, master_first, master_last, client_first, client_last in appointments:
                data.append({
                    'date': app.start_datetime.date(),
                    'service': service_name,
                    'master': f"{master_first} {master_last}",
                    'client': f"{client_first} {client_last}",
                    'price': app.service.price,
                    'status': app.status.value,
                    'duration': app.service.duration_minutes if app.service else 0
                })
            
            df = pd.DataFrame(data)
            
            if df.empty:
                print("Нет данных для статистики")
                df = pd.DataFrame(columns=['date', 'service', 'master', 'client', 'price', 'status', 'duration'])
            
            return df
            
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            return pd.DataFrame(columns=['date', 'service', 'master', 'client', 'price', 'status', 'duration'])
    
    # Создаем дашборд
    app.layout = html.Div([
        # Заголовок
        html.Div([
            html.H1("Статистика салона красоты", 
                   style={'textAlign': 'center', 'color': '#6a11cb', 
                          'marginBottom': '10px'}),
            html.P("Анализ эффективности и популярности услуг",
                  style={'textAlign': 'center', 'color': '#666'})
        ]),
        
        # Фильтр по дате

        html.Div([
            html.Label("Период анализа:", style={'marginRight': '10px'}),
            dcc.Dropdown(
                id='period-filter',
                options=[
                    {'label': '📅 За последние 7 дней', 'value': 7},
                    {'label': '📅 За последние 30 дней', 'value': 30},
                    {'label': '📅 За последние 90 дней', 'value': 90},
                    {'label': '📅 За все время', 'value': 9999}
                ],
                value=30,
                style={'width': '250px', 'display': 'inline-block'}
            ),
        ], style={'textAlign': 'center', 'margin': '30px 0'}),
        
        # Графики
        html.Div([
            dcc.Graph(id='revenue-chart'),
            dcc.Graph(id='service-popularity-chart'),
            dcc.Graph(id='master-performance-chart'),
        ]),
        
        # Статистика в цифрах
        html.Div(id='stats-numbers', style={
            'display': 'flex',
            'justifyContent': 'space-around',
            'margin': '40px 0',
            'flexWrap': 'wrap'
        }),
    ])
    
    # 4. Callback для обновления графиков
    @app.callback(
        [Output('revenue-chart', 'figure'),
         Output('service-popularity-chart', 'figure'),
         Output('master-performance-chart', 'figure'),
         Output('stats-numbers', 'children')],
        [Input('period-filter', 'value')]
    )
    def update_charts(period_days):
        df = get_statistics_data()
        
        if df.empty:
            # Пустые графики если нет данных
            empty_graph = px.scatter(title="Нет данных")
            empty_graph.update_layout(
                annotations=[dict(
                    text="Нет данных для отображения",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )]
            )
            
            stats = html.Div([
                html.H3("Ключевые показатели", style={'textAlign': 'center'}),
                html.P("Нет данных для анализа", style={'textAlign': 'center'})
            ])
            
            return empty_graph, empty_graph, empty_graph, stats
        
        # Фильтрация по датам
        cutoff_date = datetime.now().date() - timedelta(days=period_days)
        df_filtered = df[(df['date'] >= cutoff_date) & (df['date'] <= datetime.now().date())]
        
        #ГРАФИК ДОХОДОВ
        revenue_data = df_filtered[df_filtered['status'] == 'COMPLETED']
        if not revenue_data.empty:
            revenue_by_day = revenue_data.groupby('date')['price'].sum().reset_index()
            fig1 = px.line(revenue_by_day, x='date', y='price',
                          title="Динамика доходов",
                          labels={'date': 'Дата', 'price': 'Доход, руб.'},
                          markers=True)
            fig1.update_layout(hovermode='x unified')
        else:
            fig1 = px.scatter(title="Динамика доходов")
            fig1.update_layout(
                annotations=[dict(
                    text="Нет данных о доходах",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )]
            )
        
        # ПОПУЛЯРНОСТЬ УСЛУГ
        if not df_filtered.empty:
            service_counts = df_filtered['service'].value_counts().reset_index()
            service_counts.columns = ['service', 'count']
            fig2 = px.bar(service_counts, x='service', y='count',
                          title='Популярность услуг',
                          labels={'service': 'Услуга', 'count': 'Количество записей'},
                          color='count',
                          color_continuous_scale='Greens')
            fig2.update_layout(xaxis_tickangle=-45)
        else:
            fig2 = px.scatter(title="🎨 Популярность услуг")
            fig2.update_layout(
                annotations=[dict(
                    text="Нет данных об услугах",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )]
            )
        
        # ЭФФЕКТИВНОСТЬ МАСТЕРОВ
        completed_master_data = df_filtered[df_filtered['status'] == 'COMPLETED']

        if not completed_master_data.empty:
            master_stats = completed_master_data.groupby('master').agg({
                'price': 'sum',
                'service': 'count'
            }).reset_index()
            master_stats.columns = ['master', 'revenue', 'appointments']
            
            fig3 = px.scatter(master_stats, x='appointments', y='revenue',
                size=[15] * len(master_stats),
                color='master', hover_name='master',
                title='Эффективность мастеров',
                labels={'appointments': 'Количество выполненных записей',
                        'revenue': 'Выручка, руб.'},
                )
            #fig3.update_traces(marker=dict(line=dict(width=1, color='Grey')))
        else:
            fig3 = px.scatter(title="Эффективность мастеров")
            fig3.update_layout(
                annotations=[dict(
                    text="Нет данных о мастерах",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )]
            )
        
        # 4. КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ
        total_appointments = len(df_filtered)
        completed_appointments = len(df_filtered[df_filtered['status'] == 'COMPLETED'])
        total_revenue = revenue_data['price'].sum() if not revenue_data.empty else 0
        avg_revenue_per_day = total_revenue / period_days
        
        stats = html.Div([
            html.H3("Ключевые показатели", style={'textAlign': 'center', 'marginBottom': '20px'}),
            
            html.Div([
                html.Div([
                    html.H4(f"{total_appointments}", style={'color': 'purple', 'fontSize': '36px'}),
                    html.P("Всего записей", style={'color': '#666'})
                ], style={'textAlign': 'center', 'padding': '20px', 'background': '#f8f9fa', 
                         'borderRadius': '10px', 'margin': '10px', 'minWidth': '200px'}),
                
                html.Div([
                    html.H4(f"{completed_appointments}", style={'color': 'green', 'fontSize': '36px'}),
                    html.P("Выполнено", style={'color': '#666'})
                ], style={'textAlign': 'center', 'padding': '20px', 'background': '#f8f9fa',
                         'borderRadius': '10px', 'margin': '10px', 'minWidth': '200px'}),
                
                html.Div([
                    html.H4(f"{total_revenue:,.0f} ₽", style={'color': 'orange', 'fontSize': '36px'}),
                    html.P("Общий доход", style={'color': '#666'})
                ], style={'textAlign': 'center', 'padding': '20px', 'background': '#f8f9fa',
                         'borderRadius': '10px', 'margin': '10px', 'minWidth': '200px'}),
                
                html.Div([
                    html.H4(f"{avg_revenue_per_day:,.0f} ₽", style={'color': 'turquoise', 'fontSize': '36px'}),
                    html.P("Средний доход в день", style={'color': '#666'})
                ], style={'textAlign': 'center', 'padding': '20px', 'background': '#d3d3d3',
                          'margin': '10px', 'minWidth': '200px'}),
            ], style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap'})
        ])
        
        return fig1, fig2, fig3, stats
    
    # Запуск сервера в отдельном потоке
    def run_server():
        try:
            app.run(debug=False, port=8050, use_reloader=False, host='127.0.0.1')
        except Exception as e:
            print(f"Ошибка запуска сервера: {e}")
    
    # многопоточность
    thread = Thread(target=run_server, daemon=True)
    thread.start()
    
    # Даем время серверу запуститься
    time.sleep(3)

    try:
        webbrowser.open('http://localhost:8050')
        print("Дашборд открывается в браузере...")
        print("Адрес: http://localhost:8050")
    except:
        print("Откройте в браузере: http://localhost:8050")
    
    return "Дашборд запущен"

