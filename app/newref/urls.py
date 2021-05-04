from django.urls import path

from . import views

urlpatterns = [

    path('apropos/', views.apropos, name="apropos"),
    path('', views.refs, name='refs'),
    path('secret_key_check/', views.secret_key_check, name='secret_key_check'),

    path('votepage/<str:code>', views.votepage, name='votepage'),
    path('votedelete/<str:code>', views.votedelete, name='votedelete'),
    
    path('voteadmin/<str:hash>', views.voteadmin, name='voteadmin'),
    path('voteadmin_questions/<str:hash>', views.voteadmin_questions, name='voteadmin_questions'),
    path('delete_question/<str:hash>/<int:id_question>', views.delete_question, name='delete_question'),
    path('delete_option/<str:hash>/<int:id_option>', views.delete_option, name='delete_option'),    
    path('voteadmin_votants/<str:hash>', views.voteadmin_votants, name='voteadmin_votants'),
    path('delete_rawvote/<str:hash>/<int:id_rawvote>', views.delete_rawvote, name='delete_rawvote'), 
    path('voteadmin_bulletins/<str:hash>', views.voteadmin_bulletins, name='voteadmin_bulletins'),
    # path('ref/send_bulletin_test/<str:hash>', views.send_bulletin_test, name='send_bulletin_test'),

    path('test_email_sending/<str:hash>', views.test_email_sending, name='test_email_sending'),


    path('preview_bulletin/<str:hash>', views.preview_bulletin, name='preview_bulletin'),
    path('send_bulletins/<str:hash>', views.send_bulletins, name='send_bulletins'),

    path('voteadmin_depouillement/<str:hash>', views.voteadmin_depouillement, name='voteadmin_depouillement'),
    path('ref_depouillement/<str:hash>', views.ref_depouillement, name='ref_depouillement'),
    path('ref_results/<int:id_ref>', views.ref_results, name='ref_results'),
    path('communicate_results/<str:hash>', views.communicate_results, name='communicate_results'),
]