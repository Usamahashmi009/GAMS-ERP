from django.contrib import admin
from django.urls import path, include
from stockmgmt import views
from django.views.generic import RedirectView


urlpatterns = [
    # path('accounts/', include('registration.backends.default.urls')),
    # path('loginn/',include('signin.urls')),
    path('', RedirectView.as_view(url='/dashboard_L/', permanent=True)),
    path('dashboard_L/', views.dashboard_LPG, name='dashboard_Lpg'),
    path('add_stock/', views.stock_create_view, name='add_stock'),  # Replace 'add_stock' with your desired URL name

    path('home/', views.home, name='home'),
    path('list_item/', views.list_item, name="list_item"),
    path('update_items/<str:pk>/', views.update_items, name="update_items"),
    path('delete_items/<str:pk>/', views.delete_items, name="delete_items"),
    path('stock_detail/<str:pk>/', views.stock_detail, name="stock_detail"),
    # path('issue_items/<str:pk>/', views.issue_items, name="issue_items"),
    path('receive_items/<str:pk>/', views.receive_items, name="receive_items"),
    path('reorder_level/<str:pk>/', views.reorder_level, name="reorder_level"),
    path('addcompany/',views.add_itemcompany, name='addcompany'),
    path('delete_company/<int:pk>/', views.delete_company, name='delete_company'),  # Add the delete company URL
    path('edit_company/<int:pk>/', views.edit_company, name='edit_company'),
    path('setting_app/', views.Settings_app, name='Settings_app'),
    path('addvender/', views.add_vender, name='addvender'),
    path('edit_vender/<int:vender_id>/', views.edit_vender, name='edit_vender'),
    path('delete_vender/<int:vender_id>/', views.delete_vender, name='delete_vender'),
    path('addExpense/', views.add_ExpenseCategory, name='addExpense'),
    path('edit_expense_category/<int:category_id>/', views.edit_expense_category, name='edit_expense_category'),
    path('delete_expense_category/<int:category_id>/', views.delete_expense_category, name='delete_expense_category'),
    path('add-items/', views.add_CatItems, name='add-items'),
    path('addcategory/', views.add_category, name='addcategory'),

    path('editcategory/<int:pk>/', views.edit_category, name='edit_category'),
    path('deletecategory/<int:pk>/', views.delete_category, name='delete_category'),

    # path('make_sale/', views.make_sale, name='make_sale'),
    path('add_cash/', views.add_cash, name='add_cash'),
    path('action_history/', views.action_history, name='action_history'),
    path('returnitem/', views.sales_return, name='returnitem'),
    path('defective-items/', views.defective_item_list, name='defective-items'),
    path('replacement-items/', views.replacement_item, name='replacement-items'),
    path('make_sale/', views.sale_l, name='make_sale'),
    path('create-form/', views.create_form, name='create-form'),
    path('expenses/', views.expenses_list, name='expenses_list'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('Cost-of-goods/', views.CostofGoods, name='Cost-of-goods'),
    path('sales_return_list/', views.sales_return_list, name='sales_return_list'),

    path('edit_sale_return/<int:sale_id>/edit/', views.edit_sale_return, name='edit_sale_return'),
    path('delete_sale_return/<int:sale_id>/delete/', views.delete_sale_return, name='delete_sale_return'),



    path('purchase_record_list/', views.purchase_record_list, name='purchase_record_list'),
    path('sales_record_list/', views.sales_record_list, name='sales_record_list'),
    path('sales/<int:sale_id>/edit/', views.edit_sale, name='edit_sale'),
    path('sales/<int:sale_id>/delete/', views.delete_sale, name='delete_sales'),
    path('profit_loss/', views.Profit, name='profit_loss'),
    path('account_pay/', views.account_pay, name='account_pay'),
    path('pay_account_pay/<int:entry_id>/', views.pay_account_pay, name='pay_account_pay'),
    path('delete_account_pay/<int:account_pay_id>/', views.delete_account_pay, name='delete_account_pay'),
    path('stock_return/', views.stock_return, name='stock_return'),
    path('purchase_returns_records/', views.purchase_returns_records, name='purchase_returns_records'),
    path('account_receiveable/', views.account_receiveable, name='account_receiveable'),
    path('pay_account_rec/<int:sale_id>/', views.pay_account_rec, name='pay_account_rec'),
    path('delete_account_receiveable/<int:entry_id>/', views.delete_account_receiveable, name='delete_account_receiveable'),
    path('balance_sheet/', views.balance_sheet, name='balance_sheet'),
    path('get-items/', views.get_items, name='get_items'),
    path('Replace-create-form/', views.Replace_create_form, name='Replace-create-form'),
    path('Replace_sale/', views.Replace_l, name='Replace_sale'),
    path('add_Equity/', views.add_Equity, name='add_Equity'),
    path('edit_equity/<int:equity_id>/', views.edit_equity, name='edit_equity'),
    path('delete_equity/<int:equity_id>/', views.delete_equity, name='delete_equity'),
    path('get-items-by-category/', views.get_items_by_category, name='get_items_by_category'),
    # urls.py
    path('update_cash/<int:pk>/', views.update_cash, name='update_cash'),
    path('delete_cash/<int:pk>/', views.delete_cash, name='delete_cash'),
    path('update_item/<int:pk>/', views.update_CatItems, name='update_CatItems'),
    path('delete_CatItem/<int:pk>/', views.delete_CatItem, name='delete_CatItem'),
    path('daily_sales_chart/', views.daily_sales_chart, name='daily_sales_chart'),

    path('delete_all_products/',views.delete_all_products, name='delete_all_products'),

    path('update_account_payable/',views.update_account_payable, name='update_account_payable'),
    # path('pay_account_payable/', views.pay_account_payable, name='pay_account_payable'),

    path("admin/", admin.site.urls),
    path('my_new_load_item/', views.my_new_load_item, name='my_new_load_item'),  # Updated URL pattern name


    path('delete_sale_action/<int:sale_id>/',views.delete_sale_action, name='delete_sale_action'),
    # path('add_stock/', views.add_stock, name='add_stock'),


    path('get_items/', views.get_items, name='get_items'),


    #new file
    path("user_login",views.user_login,name="user_login"),
    path("signup/", views.sign_up, name="sign_up"),
    path("profile/", views.user_profile, name="user_profile"),
    path("logout/", views.user_logout, name="log_out"),
    path("changepassword/", views.user_change_password, name="changepassword"),
    path("userdetail/<int:id>", views.user_detail, name="user_detail"),
    

    


    # path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    # path('accounts/', include('django.contrib.auth.urls')),  # Use 'accounts/' as the prefix
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # path('accounts/', include('registration.backends.default.urls')),

    # path('forgot-password/', auth_views.PasswordResetView.as_view(template_name='forgot_password.html'), name='forgot_password'),
    # path('password_reset/', auth_views.PasswordResetView.as_view(), name='auth_password_reset'),
    # path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # path('list_history/', views.list_history, name='list_history'),
]