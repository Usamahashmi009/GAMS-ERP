from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from django.http import HttpResponse,HttpResponseRedirect
import csv
from django.contrib import messages
from .models import *
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, ExpressionWrapper, DecimalField,Case, When, Count
from django.db.utils import IntegrityError
from decimal import Decimal
from datetime import datetime
from django.template import RequestContext
from .templatetags.cash_tags import get_total_cash
from django.http import JsonResponse
from django.forms import formset_factory
from django.views.decorators.http import require_GET
from django.contrib.auth import authenticate ,login,logout ,update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm , PasswordChangeForm ,SetPasswordForm
from .forms import SignUpForm, EditUserprofileForm , EditAdminprofileForm
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core import serializers
from datetime import datetime, timedelta
from django.utils import timezone





@login_required
def home(request):
    if request.user.is_authenticated==True:
        title = 'Welcome: This is the Home Page'
        form = StockCreateForm()  # Create an instance of the form
        context = {
            "title": title,
            "form": form,  # Add the form to the context
        }
        return render(request, "home.html", context)
    else:
        return redirect('user_login')

def list_item(request):
    if request.user.is_authenticated == True:
        categories = Category.objects.all()
        items = Itemsmodel.objects.all()
        title = 'Stock List'
        form = StockSearchForm(request.POST or None)
        queryset = Stock.objects.all()
        context = {
            "title": title,
            "queryset": queryset,
            "form": form,
            "categories": categories,
            "items": items,
            'category_name': None,
            'item_name': None,
        }
        if request.method == 'POST':
            if form.is_valid():
                category_name = form.cleaned_data.get('category')
                item_name = form.cleaned_data.get('item_name')
                if category_name:
                    queryset = queryset.filter(category__name__icontains=category_name)
                if item_name:
                    queryset = queryset.filter(item_name__name__icontains=item_name)
                context.update({
                    'category_name': category_name,
                    'item_name': item_name,
                })
                if form['export_to_CSV'].value() == True:
                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename="List of stock.csv"'
                    writer = csv.writer(response)
                    writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY'])
                    for stock in queryset:
                        writer.writerow([stock.category.name, stock.item_name, stock.quantity])
                    return response
        context["queryset"] = queryset
        return render(request, "list_item.html", context)
    else:
        return redirect('user_login')

def daily_sales_chart(request):
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    items = Stock.objects.values('item_name__name').distinct()
    data = []
    for item in items:
        item_sales = Sale.objects.filter(
            stock__item_name__name=item['item_name__name'],
            sale_date__range=[start_date, end_date]
        ).values('sale_date__day').annotate(total_sales=Sum('sale_quantity'))
        labels = []
        values = []
        for sale in item_sales:
            labels.append(str(sale['sale_date__day']))
            values.append(sale['total_sales'])
        data.append({'item_name': item['item_name__name'], 'labels': labels, 'values': values})
    context = {'data': data}
    return render(request, 'daily_sales_chart.html', context)

def dashboard_LPG(request):
    if request.user.is_authenticated == True:
        Total_sales = 0  # Replace with your actual value
        total_sales_values = 0
        category=None
        category_sales = None
        three_months_ago = datetime.now() - timedelta(days=90)
        # Query to retrieve the data
        stock_data_trend = Stock.objects.filter(
            timestamp__gte=three_months_ago
        ).values(
            'category__name',  # Replace 'name' with the actual field name in the Category model
            'item_name__name',  # Replace 'name' with the actual field name in the Itemsmodel model
            'reorder_level'  # Include reorder level in the result
        ).annotate(
            total_quantity=Sum('quantity'),
            reorder_needed=Case(
                When(quantity__lte=F('reorder_level'), then=True),
                default=False,
                output_field=models.BooleanField(),
            )
        ).order_by('category__name', 'item_name__name')
        # Filter items that need to be reordered
        stock_data_reorder = stock_data_trend.filter(reorder_needed=True)
        total_sales_values = 0
        price = 0  # Default value
        quantity = 0  # Default value
        queryset = Stock.objects.all()
        sales = Sale.objects.all()   
        cash_in_hand = AddCash.objects.aggregate(Sum('cash'))['cash__sum']
        Total_sales = ActionHistory.objects.aggregate(Sum('sale_cash'))['sale_cash__sum']
        total_Stock = sum(stock.subtotal for stock in Stock.objects.all())
        total_stock_value = sum(stock.subtotal for stock in Stock.objects.all())
        # Calculate category-wise stock count
        category_stock_count = Stock.objects.values('category__name').annotate(total_count=Count('id'))
        # # Calculate itemized stock count
        # itemized_stock_count = Stock.objects.values('item_name__name').annotate(total_count=Count('id'))
        # Assuming 'quantity' is the field in the Stock model representing the quantity
        itemized_stock_count = Stock.objects.values('item_name__name').annotate(total_count=Count('id'), quantity=Sum('quantity')) 
        category_sales_data = Sale.objects.values('stock__category__name').annotate(total_sales=Sum('sale_quantity')) 
        for sale in sales:
            stock = sale.stock
            # Add the value of each sale to total_sales_values
            total_sales_values += sale.sale_quantity * stock.rate
        total_expense = calculate_sum_Expense()   
        Profit = (Total_sales or 0) - (total_sales_values or 0)
        Net_Profit = Profit - total_expense
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        items = Stock.objects.values('item_name__name').distinct()
        data = []
        for item in items:
            item_sales = Sale.objects.filter(
                stock__item_name__name=item['item_name__name'],
                sale_date__range=[start_date, end_date]
            ).values('sale_date__day').annotate(total_sales=Sum('sale_quantity'))
            labels = []
            values = []
            for sale in item_sales:
                labels.append(str(sale['sale_date__day']))
                values.append(sale['total_sales'])

            data.append({'item_name': item['item_name__name'], 'labels': labels, 'values': values})
            #Category wise data show
            category_sales = Stock.objects.values('category__name').annotate(
            total_sales=Sum('sale__sale_quantity'),
            total_revenue=Sum(F('sale__sale_quantity') * F('sale__rate'))       
        )   
        purchase_data = Stock.objects.all()
        sales_return_data = Sale.objects.filter(sale_quantity__lt=0)
        defective_items_data = DefectiveItem.objects.all()
        context = {
            'cash_in_hand': cash_in_hand,
            'Total_sales': Total_sales,
            'total_stock_value': total_stock_value,  # Corrected variable name
            'Net_Profit': Net_Profit,
            'category_stock_count': category_stock_count,
            'itemized_stock_count': itemized_stock_count,
            'total_Stock':total_Stock,
            'queryset':queryset,
            'sales': sales,
            'stock_data_reorder': stock_data_reorder,
            'data': data,
            'category_sales_data': category_sales_data,
            'category_sales': category_sales,
            'purchase_data': purchase_data,
            'sales_return_data': sales_return_data,
            'defective_items_data': defective_items_data,
            'stock_data_trend':stock_data_trend,
            
        }

        return render(request, 'dashboard.html', context)
    else:
        return redirect('user_login')

def update_account_payable(request):
    if request.method == 'POST':
        formac = accountForm(request.POST)
        if formac.is_valid():
            # Get the account payable value and vender from the form
            account_payable = formac.cleaned_data['account_payable']
            vender = formac.cleaned_data['vender']
            # Check if an entry with the same vender name already exists
            existing_entry = Account_payableModel.objects.filter(vender=vender).first()
            if existing_entry:
                # If the entry exists, update the account payable value
                existing_entry.account_payable += account_payable
                existing_entry.save()
            else:
                # If the entry doesn't exist, create a new entry
                Account_payableModel.objects.create(account_payable=account_payable, vender=vender)
            # Update the cash by adding the account payable
            cash = AddCash.objects.first()
            cash.cash += account_payable
            cash.save()
            return redirect('add_stock')  # Redirect to the appropriate URL
    # Handle the case when the form is not valid or when the request method is not POST
    return redirect('add_stock')



# def pay_account_payable(request):
#     if request.method == 'POST':
#         payment_form = PaymentForm(request.POST)
#         if payment_form.is_valid():
#             # Get the account payable paid value and vender from the form
#             account_payable_paid = payment_form.cleaned_data['account_payable_paid']
#             vender = request.POST.get('vender')

#             print(f"Form is valid. Account payable paid: {account_payable_paid}, Vender: {vender}")

#             # Check if an entry with the same vender name exists
#             existing_entry = Account_payableModel.objects.filter(vender=vender).first()

#             if existing_entry:
#                 # Check if the paid amount is less than or equal to the account payable
#                 if account_payable_paid <= existing_entry.account_payable:
#                     # Update the account payable value by subtracting the paid amount
#                     existing_entry.account_payable -= account_payable_paid
#                     existing_entry.save()

#                     # Update the cash by subtracting the paid amount
#                     cash = AddCash.objects.first()
#                     cash.cash -= account_payable_paid
#                     cash.save()

#                     print("Payment processed successfully.")

#                     return redirect('account_pay')  # Redirect to the appropriate URL
#                 else:
#                     # Handle the case where the paid amount is more than the account payable
#                     # You may want to add some error handling or display a message to the user
#                     payment_form = PaymentForm()
#                     error_message = "Paid amount exceeds the account payable. Please enter a valid amount."
#                     return render(request, 'account_payable.html', {'payment_form': payment_form, 'error_message': error_message})
#             else:
#                 # Handle the case where the entry doesn't exist for the provided vender
#                 # You may want to add some error handling or display a message to the user
#                 payment_form = PaymentForm()
#                 error_message = "No account payable entry found for the selected vendor. Please check and try again."
#                 return render(request, 'account_payable.html', {'payment_form': payment_form, 'error_message': error_message})
#         else:
#             # Handle the case when the form is not valid
#             # You may want to add some error handling or display a message to the user
#             print("Form is not valid.")
#             print(payment_form.errors)  # Print form errors for debugging
#             payment_form = PaymentForm()
#             error_message = "Invalid form submission. Please check the entered values and try again."
#             return render(request, 'account_payable.html', {'payment_form': payment_form, 'error_message': error_message})

#     # Handle the case when the request method is not POST
#     return redirect('add_stock')

def stock_create_view(request):
    if request.user.is_authenticated:
        form = StockCreateForm(request.POST)
        formacc = accountForm()
        if request.method == 'POST':           
            if form.is_valid():
                item_name = form.cleaned_data['item']
                category = form.cleaned_data['category']             
                quantity = form.cleaned_data['quantity']
                rate = form.cleaned_data['rate']
                product = quantity * rate
                # Save the product information to the Product model
                new_product = Product.objects.create(Product=product)
                # Check if the item with the same name, category, and rate already exists
                existing_item = Stock.objects.filter(item_name=item_name, category=category, rate=rate).first()
                if existing_item:
                    existing_item.quantity += quantity
                    existing_item.save()
                    # Update the cash by subtracting the total value and adding the account payable
                    cash = AddCash.objects.first()
                    total_value = quantity * rate
                    cash.cash -= total_value
                    # Add the account payable
                    cash.save()
                    # Create an action history entry for the stock addition
                    action_message = f'Quantity added to existing item: {item_name}'
                    action_history = ActionHistory(
                        user=request.user,
                        action_type=action_message,
                        cash=existing_item,
                    )
                    action_history.save()
                    return redirect('add_stock')
                else:
                    # If the item doesn't exist, create a new batch number
                    existing_items_same_name_category = Stock.objects.filter(item_name=item_name, category=category)
                    if existing_items_same_name_category.exists():
                        highest_batch_item = existing_items_same_name_category.order_by('-batch_number').first()
                        if highest_batch_item.batch_number and highest_batch_item.batch_number.startswith('B-'):
                            batch_number_prefix = 'B-'
                            batch_number_suffix = int(highest_batch_item.batch_number.split('-')[1]) + 1
                            batch_number = f'{batch_number_prefix}{batch_number_suffix:02d}'
                        else:
                            # Set the batch number to a default value if it doesn't follow the expected pattern
                            batch_number = 'B-01'
                    else:
                        # If no items with the same name and category exist, set the batch number to 'B-01'
                        batch_number = 'B-01'
                    # Set the batch number in the form data
                    form.instance.batch_number = batch_number
                    # Get the cleaned data from the 'item' field in the form
                    selected_item = form.cleaned_data['item']
                    # Assign the selected item to the 'item_name' field in the form instance
                    form.instance.item_name = selected_item
                    # Save the form and get the instance
                    instance = form.save()              
                    total_value = instance.quantity * instance.rate
                    cash = AddCash.objects.first()
                    total_value = instance.quantity * instance.rate
                    cash.cash -= total_value
                    cash.save()
                    action_message = f'Stock added {instance.item_name}'
                    action_history = ActionHistory(
                        user=request.user,
                        action_type=action_message,
                        cash=instance,
                    )
                    action_history.save()
                    return redirect('add_stock')  # Redirect to a success URL after successful form submission
            elif formacc.is_valid():
                # Handle formacc submission
                account_payable = formacc.cleaned_data['account_payable']
                return redirect('add_stock')
        else:
            form = StockCreateForm()
        
        products = Product.objects.all()
        sum_of_products = Product.objects.aggregate(Sum('Product'))['Product__sum'] or 0
        context = {
            "form": form,
            "products": products,
            'sum_of_products':sum_of_products,
            'formacc': formacc,
            
        }

        return render(request, 'stock_create_view.html', context)
    else:
        return redirect('user_login') # Redirect to login page if user is not authenticated

def my_new_load_item(request):  # Updated view name
    category_id = request.GET.get('category_id')
    items = Itemsmodel.objects.filter(category_id=category_id)
    data = [{'id': item.id, 'name': item.name} for item in items]
    return JsonResponse(data, safe=False)

def delete_all_products(request):
    # Delete all records from the Product model
    Product.objects.all().delete()
    return redirect('add_stock')

def get_items_by_category(request):
    if request.is_ajax() and request.method == 'GET':
        category_id = request.GET.get('category_id')
        # Retrieve item names based on the selected category
        items = Itemsmodel.objects.filter(category=category_id).values_list('name', flat=True)
        item_names = list(items)
        return JsonResponse({'items': item_names})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

def account_pay(request):
    if request.user.is_authenticated:
        # Query both fields
        account_payable_entries = Account_payableModel.objects.exclude(account_payable__isnull=True).values('id', 'account_payable', 'vender__name')
        
        context = {
            'account_payable_entries': account_payable_entries,
        }
        print('Accc', account_payable_entries)  # Print values to the console
        return render(request, "account_payable.html", context)
    else:
        return redirect('user_login')

def pay_account_pay(request, entry_id):
    if request.method == 'POST':
        entry = Account_payableModel.objects.get(id=entry_id)
        form = PaymentForm(request.POST)

        if form.is_valid():
            account_payable_paid = form.cleaned_data['account_payable_paid']

            if account_payable_paid <= entry.account_payable:
                # Subtract the paid amount from account_payable field
                entry.account_payable -= account_payable_paid
                entry.save()

                # Update cash.cash
                cash = AddCash.objects.first()
                cash.cash -= account_payable_paid
                cash.save()
            
            return redirect('account_pay')
        else:
            # Handle the case where the paid amount is greater than account_payable
            # You may want to display an error message or redirect to an error page
            return redirect('account_pay')  # Add appropriate error handling or redirect
    else:
        # Redirect if the request method is not POST
        return redirect('account_pay')

def delete_account_pay(request, account_pay_id):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return redirect('user_login')
    # Retrieve the AccountPayableModel object or return a 404 response if not found
    account_pay_entry = get_object_or_404(Account_payableModel, pk=account_pay_id)
    # Get the cash value before deletion
    cash_before_deletion = AddCash.objects.first().cash
    # Subtract the account_payable value from the cash
    cash_after_deletion = cash_before_deletion - account_pay_entry.account_payable
    # Save the updated cash value
    cash = AddCash.objects.first()
    cash.cash = cash_after_deletion
    cash.save()
    # Delete the object
    account_pay_entry.delete()
    return redirect('account_pay')

def update_items(request, pk):
    if request.user.is_authenticated==True:
        queryset = Stock.objects.get(id=pk)
        form = StockUpdateForm(instance=queryset)
        if request.method == 'POST':
            form = StockUpdateForm(request.POST, instance=queryset)
            if form.is_valid():
                # Get the original stock instance
                original_stock = Stock.objects.get(id=pk)
                # Calculate the original total value
                original_total_value = original_stock.quantity * original_stock.rate
                # Update the stock with the new values
                updated_stock = form.save()
                # Calculate the updated total value
                updated_total_value = updated_stock.quantity * updated_stock.rate
                # Calculate the difference in total value
                total_value_difference = updated_total_value - original_total_value
                # Retrieve the cash entry
                cash = AddCash.objects.first()  # You may need to adapt this to your actual cash model
                # Update the cash by adding the difference in total value
                cash.cash -= total_value_difference
                cash.save()
                # Create an action history entry for the stock update
                action_message = f'Stock updated {updated_stock.item_name}'
                action_history = ActionHistory(
                    user=request.user,
                    action_type=action_message,
                    cash=updated_stock,
                )
                action_history.save()
                messages.success(request, 'Successfully Updated')
                return redirect('/list_item')

        context = {
            'form': form
        }
        return render(request, 'update_items.html', context)
    else:
        return redirect('user_login')

def delete_items(request, pk):
    stock_instance = Stock.objects.get(id=pk)
    if request.method == 'POST':
        # Retrieve the cash entry
        cash = AddCash.objects.first()
        total_value = stock_instance.quantity * stock_instance.rate
        # Update the cash by adding back the total value
        cash.cash += total_value
        cash.save()
        # Create an action history entry for the stock deletion
        action_message = f'Stock deleted: {stock_instance.item_name}'
        action_history = ActionHistory(
            user=request.user,
            action_type=action_message,
            sale_cash=total_value,  # Assuming you have a field named sale_cash in your ActionHistory model
        )
        action_history.save()
        stock_instance.delete()  # Delete the stock item
        messages.success(request, 'Successfully Deleted')
        return redirect('/list_item')
    context = {
        'stock_instance': stock_instance,
    }
    return render(request, 'delete_items.html', context)

def stock_detail(request, pk):
	queryset = Stock.objects.get(id=pk)
	context = {
		"queryset": queryset,
	}
	return render(request, "stock_detail.html", context)

def receive_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = ReceiveForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.quantity += instance.receive_quantity
		instance.save()
		messages.success(request, "Received SUCCESSFULLY. " + str(instance.quantity) + " " + str(instance.item_name)+"s now in Store")
		return redirect('/stock_detail/'+str(instance.id))
		# return HttpResponseRedirect(instance.get_absolute_url())
	context = {
			"title": 'Reaceive ' + str(queryset.item_name),
			"instance": queryset,
			"form": form,
			"username": 'Receive By: ' + str(request.user),
		}
	return render(request, "add_items.html", context)

def reorder_level(request, pk):
    queryset = Stock.objects.get(id=pk)
    if request.method == 'POST':
        form = ReorderLevelForm(request.POST, instance=queryset)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            messages.success(request, f"Reorder level for {instance.item_name} is updated to {instance.reorder_level}")
            return redirect("/list_item")
    else:
        form = ReorderLevelForm(instance=queryset)
    context = {
        "instance": queryset,
        "form": form,
    }
    return render(request, "reorder_level.html", context)

def add_itemcompany(request):
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = AddItemCompanyForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('addcompany')
        else:
            form = AddItemCompanyForm()
        add_companies = Company.objects.all()
        context = {
            'form': form,
            'add_companies': add_companies
        }
        return render(request, 'add_company.html', context)
    else:
        return redirect('user_login')

def delete_company(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        company_name = company.name
        company.delete()
        # Additional actions or logging can be added here if needed
        return redirect('addcompany')  # Correct the redirect URL
    context = {'company': company}
    return render(request, 'delete_company.html', context)

def edit_company(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        form = AddItemCompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            # Additional actions or logging can be added here if needed
            return redirect('addcompany')  # Correct the redirect URL
    else:
        form = AddItemCompanyForm(instance=company)
    context = {'form': form, 'company': company}
    return render(request, 'edit_company.html', context)

def Settings_app (request):
    return render(request, 'settings.html')

def add_vender(request):
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = AddVenderForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('addvender')  # Redirect to the same page after adding a vendor
        else:
            form = AddVenderForm()
        vendors = Vender.objects.all()  # Fetch the list of vendors from the database
        context = {
            'form': form,
            'vendors': vendors,  # Add the vendors list to the context
        }
        return render(request, 'add_vender.html', context)
    else:
        return redirect('user_login')

def edit_vender(request, vender_id):
    if request.user.is_authenticated:
        vender = get_object_or_404(Vender, pk=vender_id)
        if request.method == 'POST':
            form = AddVenderForm(request.POST, instance=vender)
            if form.is_valid():
                form.save()
                return redirect('addvender')
        else:
            form = AddVenderForm(instance=vender)
        return render(request, 'edit_vender.html', {'form': form, 'vender': vender})
    else:
        return redirect('user_login')

def delete_vender(request, vender_id):
    if request.user.is_authenticated:
        vender = get_object_or_404(Vender, pk=vender_id)
        if request.method == 'POST':
            vender.delete()
            return redirect('addvender')
        return render(request, 'delete_vender.html', {'vender': vender})
    else:
        return redirect('user_login')

def add_ExpenseCategory(request):
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = ExpenseCatForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('addExpense')  # Redirect to the same page after adding a vendor
        else:
            form = ExpenseCatForm()
        ex = Expense.objects.all()  # Fetch the list of vendors from the database
        context = {
            'form': form,
            'ex': ex,  # Add the vendors list to the context
        }
        return render(request, 'add_ExpenseCategory.html', context)
    else:
        return redirect ('user_login')

def edit_expense_category(request, category_id):
    if request.user.is_authenticated:
        category = get_object_or_404(Expense, pk=category_id)
        if request.method == 'POST':
            form = ExpenseCatForm(request.POST, instance=category)
            if form.is_valid():
                form.save()
                return redirect('addExpense')
        else:
            form = ExpenseCatForm(instance=category)
        return render(request, 'edit_expense_category.html', {'form': form, 'category': category})
    else:
        return redirect('user_login')

def delete_expense_category(request, category_id):
    if request.user.is_authenticated:
        category = get_object_or_404(Expense, pk=category_id)
        if request.method == 'POST':
            category.delete()
            return redirect('addExpense')
        return render(request, 'delete_expense_category.html', {'category': category})
    else:
        return redirect('user_login')

def add_category(request):
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = AddCategoryForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('addcategory')  # Redirect to the same page after adding a vendor
        else:
            form = AddCategoryForm()
        category = Category.objects.all()  # Fetch the list of vendors from the database
        context = {
            'form': form,
            'category': category,
        }
        return render(request, 'add_category.html', context)
    else:
        return redirect ('user_login')

def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = AddCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('addcategory')
    else:
        form = AddCategoryForm(instance=category)
    context = {
        'form': form,
        'categories': Category.objects.all(),
    }
    return render(request, 'add_category.html', context)

def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect('addcategory')

def add_CatItems(request):
        if request.method == 'POST':
            form = AddItemsform(request.POST)
            if form.is_valid():
                form.save()
                return redirect('add-items')  # Redirect to the same page after adding a vendor
        else:
            form = AddItemsform()
        Item = Itemsmodel.objects.all()  # Fetch the list of vendors from the database
        context = {
            'form': form,
            'Item': Item,  # Add the vendors list to the context
        }
        return render(request, 'add_item_name.html', context)

def update_CatItems(request, pk):
    if request.user.is_authenticated:
        item_entry = get_object_or_404(Itemsmodel, pk=pk)
        form = UpdateItemsForm(instance=item_entry)
        if request.method == 'POST':
            form = UpdateItemsForm(request.POST, instance=item_entry)
            if form.is_valid():
                updated_item_entry = form.save()
                # Assuming item_name is a field in your Itemsmodel
                updated_item_name = updated_item_entry. name
                messages.success(request, 'Item entry updated successfully.')
                return redirect('add-items')  # Replace with the actual URL to redirect after update
        context = {
            'form': form,
            'item_entry': item_entry,
        }
        return render(request, 'update_item_name.html', context)
    else:
        return redirect('user_login')

def delete_CatItem(request, pk):
    item = get_object_or_404(Itemsmodel, pk=pk)
    if request.method == 'POST':
        item_name = item.name  # Use 'name' instead of 'item_name'
        item.delete()
        # Additional actions or logging can be added here if needed
        return redirect('add-items')  # Correct the redirect URL
    context = {'item': item}
    return render(request, 'delete_Catitem.html', context)

def sale_l(request):
    if request.user.is_authenticated==True:
        context = {'form': SaleForm()}
        return render(request, 'index.html', context)
    else:
        return redirect ('user_login')

def create_form(request): #this is make_sale function
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = SaleForm(request.POST)
            batchform = BatchForm(request.POST)
            if form.is_valid():
                stock = form.cleaned_data['stock']
                sale_quantity = form.cleaned_data['sale_quantity']
                rate = form.cleaned_data['rate']
                item_name = stock.item_name
                total_amount = sale_quantity * rate
                if sale_quantity <= stock.quantity:
                    stock.quantity -= sale_quantity
                    stock.save()  # Update the stock quantity
                    sale = form.save()
                    timestamp = datetime.now()
                    # Create an action history entry for the main sale
                    action_type = f'Sale Made - {item_name}'
                    action_history = ActionHistory(
                        user=request.user,
                        action_type=action_type,
                        sale_cash=sale_quantity * rate,
                        timestamp=timestamp
                    )
                    action_history.save()
                    # Update the cash by subtracting the main sale amount
                    cash = AddCash.objects.first()  # Get the cash entry (you may need to adapt this part)
                    cash.cash += total_amount
                    cash.cash -= sale.account_recieveable  # Use the sale's account_recieveable field
                    cash.save()
                    cogs_model_instance = COGSModel.objects.first()
                    cogs_model_instance.cogs_sum += sale_quantity * stock.rate
                    cogs_model_instance.save()
                else:
                    messages.error(request, f"INSUFFICIENT STOCK! {stock.item_name}")
            else:
                messages.error(request, "Form is not valid")
        else:
            form = SaleForm()
        return render(request, 'forms.html', {'form': form})
    else:
        return redirect ('user_login')

def account_receiveable(request):
    account_recieveable_values = Sale.objects.filter(account_recieveable__gt=0).values('id', 'account_recieveable', 'Date_time','received_by')
    context = {
        'account_recieveable_values': account_recieveable_values,
    }
    return render(request, "account_recieveable.html", context)

def pay_account_rec(request, sale_id):
    sale = Sale.objects.get(id=sale_id)

    if request.method == 'POST':
        form = Pay_recieveableForm(request.POST)

        if form.is_valid():
            account_recieveable_paid = form.cleaned_data['account_recieveable_paid']

            if account_recieveable_paid <= sale.account_recieveable:
                # Subtract the paid amount from account_recieveable field
                sale.account_recieveable -= account_recieveable_paid
                sale.save()

                # Update cash.cash
                cash = AddCash.objects.first()
                cash.cash += account_recieveable_paid
                cash.save()

                return redirect('account_receiveable')
            else:
                # Handle the case where the paid amount is greater than account_recieveable
                # You may want to display an error message or redirect to an error page
                return redirect('account_receiveable')  # Add appropriate error handling or redirect
        else:
            # Handle form validation errors
            # You may want to display an error message or redirect to an error page
            return redirect('account_receiveable')  

def edit_account_receiveable(request, entry_id):
    entry = get_object_or_404(Sale, id=entry_id)
    form = YourForm(request.POST or None, instance=entry)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('account_receiveable')
    context = {
        'form': form,
        'entry_id': entry_id,
    }
    return render(request, 'edit_account_receiveable.html', context)

def delete_account_receiveable(request, entry_id):
    entry = get_object_or_404(Sale, id=entry_id)
    if request.method == 'POST':
        entry.delete()
        return redirect('account_receiveable')
    context = {
        'entry': entry,
    }
    return render(request, 'delete_account_receiveable.html', context)

def calculate_total_cash():
    total_cash = AddCash.objects.aggregate(Sum('cash'))['cash__sum'] or 0
    return total_cash

def log_action(request, action_type, item_name=None):
    if request.user.is_authenticated:
        if item_name:
            action_type_with_item = f'{action_type} - {item_name}'
        else:
            action_type_with_item = action_type
        ActionHistory.objects.create(user=request.user, action_type=action_type_with_item)

def action_history(request):
    if request.user.is_authenticated==True:
        total_cash = calculate_total_cash()
        history_entries = ActionHistory.objects.all().order_by('-timestamp')
        total_value = 0
        for entry in history_entries:
            if entry.cash:
                entry.total_value = entry.cash.quantity * entry.cash.rate
                entry.remaining_amount = entry.total_value - total_cash
            else:
                entry.total_value = 0
                entry.remaining_amount = 0
            entry.save()
        context = {
            'history_entries': history_entries,
            'form': AddCashForm(),
            'total_cash': total_cash,
            'total_value': total_value
        }
        return render(request, 'action_history.html', context)
    else:
        return redirect ('user_login')

def add_cash(request):
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = AddCashForm(request.POST)
            if form.is_valid():
                cash_amount = form.cleaned_data['cash']
                # Save the new cash record to the database
                AddCash.objects.create(cash=cash_amount)
                action_message = f'Cash added- {cash_amount}'
                action_history = ActionHistory(
                    user=request.user,
                    action_type=action_message,
                    cash_hand=cash_amount,
                )
                action_history.save()
                return redirect('action_history')
        else:
            form = AddCashForm()
        # Calculate the total cash by summing up the 'cash' field in the AddCash model
        total_cash = AddCash.objects.aggregate(Sum('cash'))['cash__sum']
        # Query all the cash records from the database to display them on the page.
        cash_records = AddCash.objects.all()
        return render(request, 'your_template.html', {'form': form, 'cash_records': cash_records, 'total_cash': total_cash})
    else:
        return redirect ('user_login')

def update_cash(request, pk):
    if request.user.is_authenticated:
        cash_entry = get_object_or_404(AddCash, pk=pk)
        form = UpdateCashForm(instance=cash_entry)
        if request.method == 'POST':
            form = UpdateCashForm(request.POST, instance=cash_entry)
            if form.is_valid():
                original_cash_value = cash_entry.cash
                updated_cash_entry = form.save()
                updated_cash_value = updated_cash_entry.cash
                cash_difference = updated_cash_value - original_cash_value
                # Assuming cash_amount is defined somewhere in your code
                action_message = f'Cash Updated - {updated_cash_value}'
                action_history = ActionHistory(
                    user=request.user,
                    action_type=action_message,
                    cash_hand=updated_cash_value,
                )
                action_history.save()
                messages.success(request, 'Cash entry updated successfully.')
                return redirect('add_cash')  # Replace with the actual URL to redirect after update
        context = {
            'form': form,
            'cash_entry': cash_entry,
        }
        return render(request, 'update_cash.html', context)
    else:
        return redirect('user_login')

def delete_cash(request, pk):
    record = get_object_or_404(AddCash, pk=pk)
    if request.method == 'POST':
        cash_amount = record.cash  # Assuming cash_amount is defined somewhere in your code
        record.delete()
        # Assuming cash_amount is defined somewhere in your code
        action_message = f'Cash Deleted - {cash_amount}'
        action_history = ActionHistory(
            user=request.user,
            action_type=action_message,
            cash_hand=cash_amount,
        )
        action_history.save()
        return redirect('add_cash')
    context = {'record': record}
    return render(request, 'delete_cash.html', context)

def defective_item_list(request):
    if request.user.is_authenticated==True:
        defective_items = DefectiveItem.objects.all()
        title= 'Defective Items List'
        context = {
            'title':title,
            'defective_items': defective_items,
        }
        return render(request, 'defective_items.html', context)
    else:
        return redirect ('user_login')

def replacement_item(request):
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = SalesReturnForm(request.POST)
            form1 = ReplacementForm(request.POST)
            if form.is_valid() and form1.is_valid():
                batch_number = form.cleaned_data['batch_number']
                category = form.cleaned_data['category']
                item_name = form.cleaned_data['item_name']
                price = form.cleaned_data['price']
                quantity = form.cleaned_data['quantity']
                action = form.cleaned_data['action']
                # Access cleaned data from ReplacementForm
                stock_item, created = Stock.objects.get_or_create(batch_number=batch_number, category=category, item_name=item_name)
                if quantity > stock_item.quantity:
                    messages.error(request, 'Insufficient stock quantity!')
                else:
                    stock_item.quantity -= quantity
                    total_cash = AddCash.objects.first()
                    if hasattr(total_cash, 'cash'):
                        total_cash.cash += price
                        total_cash.save()
                    # Update profit in the ActionHistory model
                    action_message = f'Sale Return - {item_name}'
                    action_history = ActionHistory(
                        user=request.user,
                        action_type=action_message,
                        sale_cash=+sub_cash,
                        timestamp=datetime.now()
                    )
                    action_history.save()
                    stock_item.save()
                    title = 'Replacement'
                    context = {
                        'title': title,
                        'form1': form1,
                        'total_cash': calculate_total_cash(),
                    }
                    return render(request, 'replacement_item.html', context)
        else:
            category = None
            item_name = None
            price = None
            quantity = None
            action = None
            form = SalesReturnForm()
            form1 = ReplacementForm()
            title = 'Replacement'
            context = {
                'title': title,
                'form1': form1,
                'total_cash': calculate_total_cash(),
            }
            return render(request, 'replacement_item.html', context)
        return render(request, 'replacement_item.html', {'form': form, 'form1': form1})
    else:
        return redirect ('user_login')

def stock_return(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = StockReturnForm(request.POST)
            if form.is_valid():
                stock = form.cleaned_data['stock']
                return_quantity = form.cleaned_data['return_quantity']
                # Check if there is enough stock to return
                if stock.quantity < return_quantity:
                    return render(request, 'stock_return.html', {'form': form, 'error_message': 'Not enough stock to return.'})
                # Create a StockReturn entry
                stock_return_entry = StockReturn.objects.create(stock=stock, return_quantity=return_quantity)
                # Update the stock quantity
                stock.quantity -= return_quantity
                stock.save()
                # Calculate the total value returned
                total_value_returned = stock_return_entry.return_quantity * stock.rate  # Adjust this based on your model
                # Adjust the cash
                cash_entry = AddCash.objects.first()
                if cash_entry:
                    cash_entry.cash += total_value_returned
                    cash_entry.save()
                # Add a success message
            messages.success(request, 'Stock returned successfully!')
        else:
            form = StockReturnForm()
        return render(request, 'stock_return.html', {'form': form})
    else:
        return redirect('user_login')

def purchase_returns_records(request):
    purchase_returns = StockReturn.objects.all()
    for purchase_return in purchase_returns:
        purchase_return.total_value_returned = purchase_return.stock.rate * purchase_return.return_quantity
    context = {
        'purchase_returns': purchase_returns,
    }
    return render(request, 'purchase_returns_records.html', context)

def sales_return_list(request):
    if request.user.is_authenticated:
        # Filter only the returned items (negative sale_quantity)
        sales_data = Sale.objects.filter(sale_quantity__lt=0)
        
        context = {
            'sales_data': sales_data,
        }
        return render(request, 'sales_return_list.html', context)
    else:
        return redirect('user_login')

def edit_sale_return(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    original_sale_quantity = sale.sale_quantity
    original_sale_price = sale.rate
    var1 = original_sale_price*original_sale_quantity
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            updated_sale_quantity = form.cleaned_data['sale_quantity']
            updated_sale_rate = form.cleaned_data['rate']
            var2 = updated_sale_rate*updated_sale_quantity
            var3 = var2 - var1
            total_difference = original_sale_quantity - updated_sale_quantity
            total_difference_cash = original_sale_price - updated_sale_rate
            sale.stock.quantity += total_difference
            cash= AddCash.objects.first()
            cash.cash+=var3
            sale_Action = ActionHistory.objects.first()
            sale_Action.sale_cash+=var3
            sale_Action.save()
            cash.save()
            sale.save()
            sale.stock.save()           
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sale updated successfully.')
            return redirect('sales_return_list')
    else:
        form = SaleForm(instance=sale)
    return render(request, 'edit_sale_return.html', {'form': form, 'sale': sale})

def delete_sale_return(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    cash_in_hand_record = AddCash.objects.first()
    stock = sale.stock
    if request.method == 'POST':
        sale_quantity = sale.sale_quantity
        rate = sale.rate
        defective_item = DefectiveItem.objects.filter(category=sale.stock.category, item_name=sale.stock.item_name, batch_number=sale.stock.batch_number).first()
        # Check if both sale_quantity and rate are non-negative
        if sale_quantity <= 0 and rate >= 0:
            if defective_item:
                defective_item.delete()
                AddCash.objects.update(cash=F('cash') - sale_quantity * rate)
            else:
                stock.quantity -= abs(sale_quantity)
                # If either is negative, add the absolute value to cash_in_hand
                AddCash.objects.update(cash=F('cash') - abs(sale_quantity) * abs(rate))
        stock.save()
        # Check if the sale has an associated defective item
        sale.delete()
        messages.success(request, 'Sale deleted successfully.')
        return redirect('sales_return_list')
    return render(request, 'delete_sale_return.html', {'sale': sale})

def purchase_record_list(request):
    purchase_data = Stock.objects.all()
    return render(request, 'purchase_record_list.html', {'purchase_data': purchase_data})

def sales_record_list(request):
    sales_data = Sale.objects.filter(sale_quantity__gte=0)
    context = {
        'sales_data': sales_data,     
    }
    return render(request, 'sales_record_list.html', context)

def edit_sale(request, sale_id):
    if request.user.is_authenticated:
        sale = get_object_or_404(Sale, id=sale_id)
        original_sale_quantity = sale.sale_quantity
        original_sale_price = sale.rate
        var1 = original_sale_price*original_sale_quantity
        if request.method == 'POST':
            form = SaleForm(request.POST, instance=sale)
            if form.is_valid():
                updated_sale_quantity = form.cleaned_data['sale_quantity']
                updated_sale_rate = form.cleaned_data['rate']
                var2 = updated_sale_rate*updated_sale_quantity
                var3 = var2 - var1
                total_difference = original_sale_quantity - updated_sale_quantity
                total_difference_cash = original_sale_price - updated_sale_rate
                sale.stock.quantity += total_difference
                cash= AddCash.objects.first()
                cash.cash+=var3
                sale_Action = ActionHistory.objects.first()
                sale_Action.sale_cash+=var3
                sale_Action.save()
                cash.save()
                sale.save()
                sale.stock.save()
                return redirect('sales_record_list')  # Redirect to the sales record list or another appropriate page
            else:
                messages.error(request, "Form is not valid. Please check your inputs.")
        else:
            form = SaleForm(instance=sale)
        return render(request, 'edit_sale.html', {'form': form, 'sale': sale})
    else:
        return redirect('user_login')

def delete_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    stock = sale.stock 
    cash_in_hand_record = AddCash.objects.first()  # Assuming there is only one record for cash in hand
    if request.method == 'POST':
        sale_quantity = sale.sale_quantity
        rate = sale.rate
        # Check if sale_quantity or rate is negative
        if sale_quantity < 0 or rate < 0:
            stock.quantity += abs(sale_quantity)  # Add the absolute value to quantity
            # If either is negative, add the absolute value to cash_in_hand
            AddCash.objects.update(cash=F('cash') + abs(sale_quantity) * abs(rate))
            stock.save()
        else:
            stock.quantity += sale_quantity  # Add to quantity
            # If both are positive or zero, subtract from cash_in_hand
            AddCash.objects.update(cash=F('cash') - sale_quantity * rate)
            stock.save()
        defective_item = DefectiveItem.objects.filter(category=sale.stock.category, item_name=sale.stock.item_name, batch_number=sale.stock.batch_number).first()
        if defective_item:
            defective_item.delete()
        sale.delete()
        return redirect('sales_record_list')  # Redirect to the sales record list page
    return render(request, 'delete_sale.html', {'sale': sale})

def add_expense(request):
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = AddExpenseForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data['amount']
                form.save()
                total_cash = AddCash.objects.first()
                total_cash.cash -= amount  # Subtract the amount from the cash attribute
                total_cash.save()
        else:
            form = AddExpenseForm()
        return render(request, 'add_expense.html', {'form': form})
    else:
        return redirect ('user_login')

def expenses_list(request):
    if request.user.is_authenticated==True:
        expenses = Expenses.objects.all()
        return render(request, 'expenses_list.html', {'expenses': expenses})
    else:
        return redirect('user_login')

def total_sales (request):
    total_sales = ActionHistory.objects.aggregate(Sum('sale_cash'))['sale_cash__sum'] or 0
    return total_sales

def total_cogs (request):
    total_values_sum = sum(item['total_values'] for item in total_values_list)
    return total_values_sum

def CostofGoods(request):
    if request.user.is_authenticated:
        # Assuming you have a Sale model with a ForeignKey to Stock
        sales = Sale.objects.all()
        total_values_sum = 0  # Initialize the total values sum
        for sale in sales:
            stock = sale.stock
            total_values_sum += sale.sale_quantity * stock.rate  # Accumulate total values sum
            # Optionally, you can add the calculated total values to each sale instance
            sale.total_values = sale.sale_quantity * stock.rate
        # Consider sales returns from the form
        if request.method == 'POST':
            form = SalesReturnForm(request.POST)
            if form.is_valid():
                category = form.cleaned_data['category']
                item_name = form.cleaned_data['item_name']
                quantity = form.cleaned_data['quantity']
                action = form.cleaned_data['action']
            total_values_sum -= quantity * stock_returned.rate
            
        context = {
            'total_values_sum': total_values_sum,
            'all_sales': sales,  # Include all sales records in the context
        }
        return render(request, 'CostofGoods.html', context)
    else:
        return redirect('user_login')

def calculate_sum_Expense():
    total_expense = Expenses.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    return total_expense

def sales_return(request):
    total_sales_values = 0
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = SalesReturnForm(request.POST)
            if form.is_valid():
                batch_number = form.cleaned_data['batch_number']
                category = form.cleaned_data['category']
                item_name = form.cleaned_data['item_name']
                price = form.cleaned_data['price']
                quantity = form.cleaned_data['quantity']
                action = form.cleaned_data['action']
                # Use filter instead of get to handle multiple objects
                stock_queryset = Stock.objects.filter(category=category, item_name=item_name, batch_number=batch_number)
                if stock_queryset.exists():
                    stock = stock_queryset.first()  # You can choose any logic here based on your requirements
                else:
                    # Handle the case when no Stock object is found
                    # You might want to add appropriate error handling or redirect the user
                    return HttpResponse("Stock not found for the specified criteria.")
                if action == 'defective':
                    # Store the item in the Defective database
                    defective_item = DefectiveItem(
                        batch_number=batch_number,
                        category=category,
                        item_name=item_name,
                        price=price,
                        quantity=quantity,
                        stock=stock  # Add this line to associate DefectiveItem with Stock
                    )
                    defective_item.save()
                    total_cash = AddCash.objects.first()
                    if hasattr(total_cash, 'cash'):
                        total_cash.cash -= price * quantity
                        total_cash.save()
                    # Handling defective item related code
                    deducted_amount = stock.rate * quantity
                    list_deduct = {deducted_amount}
                    sales = Sale(
                        stock=stock,
                        sale_quantity=-quantity,
                        rate=price
                    )
                    sales.save()
                    return_amount = price * quantity
                    action_message = f'Sale Return - {item_name}'
                    action_history = ActionHistory(
                        user=request.user,
                        action_type=action_message,
                        sale_cash=-return_amount,
                        timestamp=datetime.now()
                    )
                    action_history.save()
                    return redirect('/list_item')
                else:
                    total_cash = AddCash.objects.first()
                    if hasattr(total_cash, 'cash'):
                        total_cash.cash -= price * quantity
                        total_cash.save()
                    # Add quantity to the related database
                    stock_item, created = Stock.objects.get_or_create(batch_number=batch_number, category=category, item_name=item_name)
                    stock_item.quantity += quantity
                    stock_item.save()
                    # Calculate the return amount
                    cogs_model_instance = COGSModel.objects.first()
                    if cogs_model_instance is None:
                        cogs_model_instance = COGSModel.objects.create(cogs_sum=0)
                    cogs_model_instance.cogs_sum -= stock_item.rate * quantity
                    cogs_model_instance.save()
                    deducted_amount = price * quantity
                    deducted_amount_defective = stock.rate * quantity
                    list_deductto = {deducted_amount_defective}
                    if cogs_model_instance is not None:
                        total_cogs = cogs_model_instance.cogs_sum
                    else:
                        total_cogs = 0
                    sales = Sale(
                        stock=stock,
                        sale_quantity=-quantity,
                        rate=price 
                    )
                    sales.save()
                    return_amount = price * quantity
                    action_message = f'Sale Return - {item_name}'
                    action_history = ActionHistory(
                        user=request.user,
                        action_type=action_message,
                        sale_cash=-return_amount,
                        timestamp=datetime.now()
                    )
                    action_history.save()
                return redirect('/list_item')
        else:
            form = SalesReturnForm()
        context = {
            'form': form,
        }
        return render(request, 'sales_return.html', context)
    else:
        return redirect('user_login')

def Profit(request):
    total_values = 0
    price = 0  # Default value
    quantity = 0  # Default value
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = SalesReturnForm(request.POST)
            if form.is_valid():
                price = form.cleaned_data['price']
                quantity = form.cleaned_data['quantity']
        total_sales_value = total_sales(request)
        sales = Sale.objects.all()
        for sale in sales:
            stock = sale.stock
            total_values += sale.sale_quantity * stock.rate
        total_expense = calculate_sum_Expense()
        cogs_model_instance = COGSModel.objects.first()
        if cogs_model_instance is not None:
            total_cogs = cogs_model_instance.cogs_sum
        else:
            total_cogs = 0       
     # Calculate the sum of sale.quantity * sale.rate
        Total_sales = sales.aggregate(total_sum=Sum(F('sale_quantity') * F('rate')))['total_sum'] or 0
        deducted_amount = price * quantity
        total_values -= deducted_amount
        Profit = Total_sales - total_values
        Net_Profit = Profit - total_expense
        context = {
            "total_sales_value": Total_sales,
            "COGS_sum": total_values,
            'GrossP': Profit,
            'total_expense': total_expense,
            'Net_Profit': Net_Profit,
        }
        return render(request, 'Profit_loss.html', context)
    else:
        return redirect('user_login')

@require_GET
def get_categories(request):
    batch_number = request.POST.get('batch_number')
    categories = YourModel.objects.filter(batch_number=batch_number).values_list('category', flat=True).distinct()
    return JsonResponse({'categories': list(categories)})

def sign_up(request):
    if request.method =="POST":
        fm = SignUpForm(request.POST)
        if fm.is_valid():
            messages.success(request,"Account created successfully::")
            fm.save()
            return HttpResponseRedirect("/signup/")
    else:
        fm = SignUpForm()
    context={
        "form":fm
    }
    return render(request, 'signin/signup.html', context)

def user_login(request):
    if not request.user.is_authenticated:
        if request.method =="POST":
            fm = AuthenticationForm(request=request,data = request.POST)
            if fm.is_valid():
                user_name = fm.cleaned_data['username']
                user_password = fm.cleaned_data['password']
                user = authenticate(username=user_name,password=user_password)
                if user is not None:
                    login(request, user)
                    return HttpResponseRedirect("/dashboard_L")
        else:
            fm = AuthenticationForm()
        context={
            "form":fm
            }
        return render(request, 'signin/userlogin.html', context)
    else:
        return HttpResponseRedirect("/home")

def user_profile(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            if request.user.is_superuser == True:
                fm =EditAdminprofileForm(request.POST , instance = request.user)
                users = User.objects.all()
            else:
                fm =EditUserprofileForm(request.POST , instance = request.user)
                users = None
            if fm.is_valid():
                messages.success(request, "profile successfully updated !!!")
                fm.save()
        else:
            if request.user.is_superuser == True:
                fm = EditAdminprofileForm(instance = request.user)
                users = User.objects.all()
            else:
                fm = EditUserprofileForm(instance = request.user)
                users = None
            # fm =EditUserprofileForm(instance = request.user)
        context={
            "name": request.user.username,
            "form":fm,
            "users":users
        }
        return render(request, "signin/profile.html", context)
    else:
        return HttpResponseRedirect("/login/")

def user_logout(request):
    logout(request)
    return redirect("user_login")

def user_change_password(request):
    # password2 = forms.CharField(label="Confirm password (again) ",widget= forms.PasswordInput)
    if request.user.is_authenticated:
        if request.method == "POST":
            fm =PasswordChangeForm(user = request.user , data=request.POST)
            if fm.is_valid():
                fm.save()
                update_session_auth_hash(request , fm.user)
                messages.success(request,"Passwaor changed successfully::")
                return HttpResponseRedirect("/profile/")
        else:
            fm =PasswordChangeForm(user = request.user)
        context= {
            "form":fm
        }
        return render (request, "signin/changepassword.html", context)
    else:
        return HttpResponseRedirect("/login/")

def user_detail(request , id):
    if request.user.is_authenticated:
        pi  = User.objects.get(pk=id)
        fm = EditAdminprofileForm(instance = pi)
        context = {
            "form":fm
        }
        return render(request , "signin/userdetail.html",context)
    else:
        return HttpResponseRedirect("/login/")

def Replace_l(request):
    if request.user.is_authenticated==True:
        context = {'form': ReplacementSaleForm()}
        return render(request, 'indexsale.html', context)
    else:
        return redirect ('user_login')

def Replace_create_form(request):
    if request.user.is_authenticated==True:
        if request.method == 'POST':
            form = ReplacementSaleForm(request.POST)
            batchform = BatchForm(request.POST)
            if form.is_valid():
                stock = form.cleaned_data['stock']
                sale_quantity = form.cleaned_data['sale_quantity']
                rate = form.cleaned_data['rate']
                cash_adjust = form.cleaned_data['cash_adjust']
                item_name = stock.item_name
                # total_amount = sale_quantity * rate
                if sale_quantity <= stock.quantity:
                    stock.quantity -= sale_quantity
                    stock.save()  # Update the stock quantity
                    sale = form.save()
                    timestamp = datetime.now()
                    # total = request.session.get('total_values_sum', 0) + cash_adjust
                    # Create an action history entry for the main sale
                    amount = sale_quantity*rate
                    print('Rate:', rate)
                    amount -= cash_adjust
                    total = request.session['COGS_sum'] - amount
                    print('Total COGS', total)
                    # totatl.save()
                    print('Cash adjust:', sale_quantity)
                    print('The amount:', amount)
                    action_type = f'Replace Made - {item_name}'
                    action_history = ActionHistory(
                        user=request.user,
                        action_type=action_type,
                        sale_cash=amount,
                        timestamp=timestamp
                    )
                    action_history.save()
                    # Update the cash by subtracting the main sale amount
                    cash = AddCash.objects.first()  # Get the cash entry (you may need to adapt this part)
                    cash.cash += amount
                    cash.cash -= sale.account_recieveable  # Use the sale's account_recieveable field
                    cash.save()
                else:
                    messages.error(request, f"INSUFFICIENT STOCK! {stock.item_name}")
            else:
                messages.error(request, "Form is not valid")
        else:
            form = ReplacementSaleForm()
        return render(request, 'formsSale.html', {'form': form})
    else:
        return redirect ('user_login')

def get_items(request):
    category_id = request.GET.get('category_id')
    items = Itemsmodel.objects.filter(category_id=category_id).values()
    item_list = list(items)
    return JsonResponse(item_list, safe=False)

def delete_sale_action(request, sale_id):
    qoute = get_object_or_404(ActionHistory, pk=sale_id)
    if request.method == 'POST':
        qoute.delete()
        return redirect('action_history')
    context = {
        'qoute': qoute,
    }
    return render(request, 'action_history.html', context)

def add_Equity(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = OwnerEquityeForm(request.POST)  # Corrected the form name
            if form.is_valid():
                capital_amount = form.cleaned_data['capital']
                # Save the new equity record to the database
                OwnerEquity.objects.create(capital=capital_amount)
                # Add the equity amount to the cash
                AddCash.objects.create(cash=capital_amount)
                action_message = f'Owner Equity- {capital_amount}'
                action_history = ActionHistory(
                    user=request.user,
                    action_type=action_message,
                    cash_hand=capital_amount,
                )
                action_history.save()
        else:
            form = OwnerEquityeForm()
        # Calculate the total equity by summing up the 'capital' field in the OwnerEquity model
        total_equity = OwnerEquity.objects.aggregate(Sum('capital'))['capital__sum']
        # Query all the equity records from the database to display them on the page.
        equity_records = OwnerEquity.objects.all()
        return render(request, 'OwnerEquity.html', {'form': form, 'equity_records': equity_records, 'total_equity': total_equity})
    else:
        return redirect('user_login')

def edit_equity(request, equity_id):
    if request.user.is_authenticated:
        equity = get_object_or_404(OwnerEquity, pk=equity_id)
        if request.method == 'POST':
            form = OwnerEquityeForm(request.POST, instance=equity)
            if form.is_valid():
                form.save()
                messages.success(request, 'Equity record updated successfully.')
                return redirect('add_Equity')
        else:
            form = OwnerEquityeForm(instance=equity)
        return render(request, 'edit_equity.html', {'form': form, 'equity': equity})
    else:
        return redirect('user_login')

def delete_equity(request, equity_id):
    if request.user.is_authenticated:
        equity = get_object_or_404(OwnerEquity, pk=equity_id)
        if request.method == 'POST':
            equity.delete()
            messages.success(request, 'Equity record deleted successfully.')
            return redirect('add_Equity')
        return render(request, 'delete_equity.html', {'equity': equity})
    else:
        return redirect('user_login')

def balance_sheet(request):
    if request.user.is_authenticated:
        defective = DefectiveItem.objects.all()
        total_sales_values = 0
        price = 0  # Default value
        quantity = 0  # Default value
        profit = 0      
        sales = Sale.objects.all()
        if request.method == 'POST':
            form = SalesReturnForm(request.POST)
        deducted_amount = request.session.get('deducted_amount', 0)
        deducted_amount_defective = request.session.get('deducted_amount_defective', 0)
        for sale in sales:
            stock = sale.stock
            # Add the value of each sale to total_values
            total_sales_values += sale.sale_quantity * stock.rate
        total_expense = calculate_sum_Expense()
        cogs_model_instance = COGSModel.objects.first()
        # Calculate COGS_sum based on the current value in cogs_model_instance
        if cogs_model_instance is not None:
            total_values = cogs_model_instance.cogs_sum
        else:
            # Handle the case when there is no COGSModel instance
            total_values = 0
        total_equity = OwnerEquity.objects.aggregate(Sum('capital'))['capital__sum'] or 0
        total_Stock = sum(stock.subtotal for stock in Stock.objects.all())
        total_accountRecievable = Sale.objects.aggregate(Sum('account_recieveable'))['account_recieveable__sum'] or 0
        total_accountPayable = Account_payableModel.objects.aggregate(Sum('account_payable'))['account_payable__sum'] or 0
        cash_in_hand = AddCash.objects.aggregate(Sum('cash'))['cash__sum'] or 0
        Total_sales = sales.aggregate(total_sum=Sum(F('sale_quantity') * F('rate')))['total_sum'] or 0        
        total_sum = defective.aggregate(total_sum=Sum(F('stock__rate') * F('quantity')))['total_sum'] or 0
        total_sales_values-=deducted_amount
        total_sales_values-=deducted_amount_defective
        Profit = (Total_sales or 0) - (total_sales_values or 0)
        Net_Profit = Profit - total_expense 
        context = {
            'total_equity':total_equity,
            'total_Stock':total_Stock,
            'total_accountRecievable':total_accountRecievable,
            'total_accountPayable':total_accountPayable,
            'cash_in_hand':cash_in_hand,
            'Total_sales':Total_sales,
            'Net_Profit':Net_Profit,
            'total_sum': total_sum if total_sum is not None else 0,
        }
        return render(request, 'balance_sheet.html', context)
    else:
        return redirect('user_login')
