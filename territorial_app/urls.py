from django.urls import path, include
from . import views
from incidencias import views as incidencias_views

app_name = "territorial_app"
urlpatterns = [
                                                                                         
    path("territorial/<int:pk>/validar_incidencia/", views.validar_incidencia, name="validar_incidencia"),
    path("territorial/<int:pk>/rechazar_incidencia/", views.rechazar_incidencia, name="rechazar_incidencia"),
    path("territorial/<int:pk>/reasignar_incidencia/", views.reasignar_incidencia, name="reasignar_incidencia"),
    path("territorial/<int:pk>/finalizar_incidencia/", views.finalizar_incidencia, name="finalizar_incidencia"),
    path("incidencias/", incidencias_views.incidencias_lista, name="incidencias_lista"),
    path("incidencias/editar", incidencias_views.incidencia_editar, name="incidencia_editar"),

                           
                                                  
                               
                                                  
                      
    path("encuestas/", views.encuestas_lista, name="encuestas_lista"),
    
                    
    path("encuestas/nueva/", views.encuesta_crear, name="encuesta_crear"),
    
                              
    path('encuestas/<int:encuesta_id>/', views.encuesta_detalle, name='encuesta_detalle'),

                     
    path("encuestas/<int:pk>/editar/", views.encuesta_editar, name="encuesta_editar"),
    
                                               
    path("encuestas/<int:pk>/toggle/", views.encuesta_toggle_estado, name="encuesta_toggle_estado"),
    
                       
    path("encuestas/<int:pk>/eliminar/", views.encuesta_eliminar, name="encuesta_eliminar"),

                             
    path('encuestas/<int:encuesta_id>/pregunta/nueva/', views.pregunta_agregar, name='pregunta_agregar'),

    path('encuesta/<int:encuesta_id>/incidencia/<int:incidencia_id>/responder/', views.responder_encuesta, name='responder_encuesta'),
                                                           
    path('encuestas/json_preguntas/', views.json_preguntas, name='json_preguntas'),

                                                          
                             

    path('encuestas/<int:encuesta_id>/evidencia/subir/', 
         views.evidencia_subir, 
         name='evidencia_subir'),
         
    path('evidencia/<int:evidencia_id>/eliminar/', 
         views.evidencia_eliminar, 
         name='evidencia_eliminar'),

]
