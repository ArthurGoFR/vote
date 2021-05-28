from django.urls import path

from . import views

urlpatterns = [

    path('apropos/', views.apropos, name="apropos"),
    path('', views.refs, name='refs'),
    path('rsa_display/<str:hash>', views.rsa_display, name='rsa_display'),
    path('rsa_delete/<str:hash>', views.rsa_delete, name='rsa_delete'),
    path('secret_key_check/', views.secret_key_check, name='secret_key_check'),

    path('votepage/<str:code>', views.votepage, name='votepage'),
    path('votedelete/<str:code>', views.votedelete, name='votedelete'),
    
    path('voteadmin/<str:hash>', views.voteadmin, name='voteadmin'),
    path('voteadmin_questions/<str:hash>', views.voteadmin_questions, name='voteadmin_questions'),
    path('delete_question/<str:hash>/<int:id_question>', views.delete_question, name='delete_question'),
    path('delete_option/<str:hash>/<int:id_option>', views.delete_option, name='delete_option'),  
    path('moveup_question/<str:hash>/<int:id_question>', views.moveup_question, name='moveup_question'),
    path('moveup_option/<str:hash>/<int:id_option>', views.moveup_option, name='moveup_option'), 
    path('edit_question/<str:hash>/<int:id_question>', views.edit_question, name='edit_question'),
    path('edit_option/<str:hash>/<int:id_option>', views.edit_option, name='edit_option'),

    path('voteadmin_votants/<str:hash>', views.voteadmin_votants, name='voteadmin_votants'),
    path('delete_rawvote/<str:hash>/<int:id_rawvote>', views.delete_rawvote, name='delete_rawvote'), 
    path('delete_all_rawvotes/<str:hash>', views.delete_all_rawvotes, name='delete_all_rawvotes'), 


    path('voteadmin_bulletins/<str:hash>', views.voteadmin_bulletins, name='voteadmin_bulletins'),
    
    # path('ref/send_bulletin_test/<str:hash>', views.send_bulletin_test, name='send_bulletin_test'),

    path('test_email_sending/<str:hash>', views.test_email_sending, name='test_email_sending'),


    path('preview_bulletin/<str:hash>', views.preview_bulletin, name='preview_bulletin'),
    path('send_bulletins/<str:hash>', views.send_bulletins, name='send_bulletins'),

    path('not_received_bul/<str:hash>/<int:id_rawvote>', views.not_received_bul, name='not_received_bul'),

    path('voteadmin_depouillement/<str:hash>', views.voteadmin_depouillement, name='voteadmin_depouillement'),
    path('voteadmin_depouillement_anticipe/<str:hash>', views.voteadmin_depouillement_anticipe, name='voteadmin_depouillement_anticipe'),

    path('ref_depouillement/<str:hash>', views.ref_depouillement, name='ref_depouillement'),
    path('ref_results/<int:id_ref>', views.ref_results, name='ref_results'),
    path('communicate_results/<str:hash>', views.communicate_results, name='communicate_results'),
]