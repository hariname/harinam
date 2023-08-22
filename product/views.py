import io

from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from party.models import Party
from xlsxwriter.workbook import Workbook

from .models import Category, Product, UpdateProduct, TransactionDetails


# Create your views here.
def add_product(request):
    if request.method == 'POST':
        form = request.POST
        form_image = request.FILES
        productName = form.get('productName')
        productName = productName.upper()
        productCode = form.get('productCode')
        productCode = productCode.upper()
        productCategory = form.get('productCategory')
        productDescription = form.get('productDescription')
        purchasePrice = form.get('purchasePrice')
        salePrice = form.get('salePrice')
        OpenStock = form.get('OpenStock')
        productImage = form_image.get('productImage')

        obj = Product.objects.create(product_name=productName,
                                         code=productCode,
                                         category_id=productCategory,
                                         desc=productDescription,
                                         purchase_price=purchasePrice,
                                         sale_price=salePrice,
                                         open_stock=OpenStock,
                                         present_stock=OpenStock,
                                         )

        if obj:
            msg = 'Product Added Successful!'
        else:
            msg = 'Product Add failed.'
        json_data = {'msg': msg}
        return JsonResponse(json_data)

        # if product:
        #     if productImage:
        #         product.image = productImage
        #         product.save()
        #     return redirect('/product/productLIST/')
    else:
        category = Category.objects.all()
        context = {
            'category': category
        }
        return render(request, 'add_product.html', context)


def search_product(request):
    if request.method == 'GET':
        code = request.GET.get('code')
        product = Product.objects.filter(Q(code__iexact=code) | Q(product_name__iexact=code))
        # product_list = []
        data_dict = {}
        for product in product:
            data_dict['p_id'] = product.id
            data_dict['p_name'] = product.product_name
            data_dict['p_code'] = product.code
            data_dict['p_sale_price'] = product.sale_price
            data_dict['p_qty'] = product.present_stock if product.present_stock else 0

        length = len(data_dict)
        json_data = {
            'length': length,
            'product': data_dict,
        }
        return JsonResponse(json_data)


def edit_product(request, id):
    if request.method == 'POST':
        form = request.POST
        form_image = request.FILES
        productName = form.get('productName')
        productName = productName.upper()

        productCode = form.get('productCode')
        productCode = productCode.upper()

        productCategory = form.get('productCategory')
        productDescription = form.get('productDescription')
        purchasePrice = form.get('purchasePrice')
        salePrice = form.get('salePrice')
        # OpenStock = form.get('OpenStock')
        addStock = form.get('addStock')
        productImage = form_image.get('productImage')

        productHist = Product.objects.get(id=id)

        product = Product.objects.filter(id=id).update(product_name=productName,
                                                       code=productCode,
                                                       category_id=productCategory,
                                                       desc=productDescription,
                                                       purchase_price=purchasePrice,
                                                       present_stock=int(productHist.present_stock) + int(addStock),
                                                       sale_price=salePrice,
                                                       # open_stock=OpenStock,
                                                       )
        if product:
            UpdateProduct.objects.create(product_id=id,
                                         open_stock=productHist.open_stock,
                                         present_stock=productHist.present_stock,
                                         add_stock_qty=addStock,
                                         total_present_stock=int(productHist.present_stock) + int(addStock),
                                         )

        if product:
            if productImage:
                product.image = productImage
                product.save()
            msg = 'success'
            return redirect(f'/product/edit-product/{id}/')
    else:
        product = Product.objects.get(id=id)
        pro_cat = product.category
        category = Category.objects.all().exclude(name=pro_cat)
        context = {
            'product': product,
            'category': category
        }
        return render(request, 'edit_product.html', context)


def delete_product(request, id):
    try:
        Product.objects.filter(id=id).delete()
    except:
        pass
    return redirect('/product/productLIST/')


def product_list(request):
    product = Product.objects.all()
    context = {
        'product': product
    }
    return render(request, 'productLIST.html', context)


def export_party(request, fromD, toD, search):
    output = io.BytesIO()
    workbook = Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('party')

    header_format = workbook.add_format({
        'border': 1,
        'bg_color': '#C6EFCE',
        'bold': True,
        'text_wrap': True,
        'valign': 'vcenter',
        'indent': 1,
    })

    headings = ['Party Name', 'Address', 'Email', 'Contact No.', 'date']
    for col_num, heading in enumerate(headings):
        worksheet.write(0, col_num, heading, header_format)

    unlocked_format = workbook.add_format({'locked': False})
    worksheet.set_column('A:A', 35, unlocked_format)
    worksheet.set_column('B:B', 25, unlocked_format)
    worksheet.set_column('C:C', 25, unlocked_format)
    worksheet.set_column('D:D', 25, unlocked_format)
    worksheet.set_column('E:E', 25, unlocked_format)

    # worksheet.protect()

    if fromD != 'None':
        party_data = Party.objects.filter(Q(date__date=fromD))

    if fromD != 'None' and toD != 'None':
        party_data = Party.objects.filter(Q(date__date__gte=fromD) & Q(date__date__lte=toD))
    if search != 'None':
        party_data = Party.objects.filter(
            Q(customer_name__iexact=search) | Q(email__iexact=search) | Q(phone_no__iexact=search))

    if fromD == 'None' and toD == 'None' and search == 'None':
        party_data = Party.objects.all()

    rows = []
    for loop_counter, obj in enumerate(party_data):
        name = obj.customer_name
        contact = obj.phone_no
        address = obj.address
        email = obj.email
        date = obj.date.strftime("%Y-%m-%d")

        rows.append([name, address, email, contact, date])

    for row_num, row_data in enumerate(rows, start=1):
        for col_num, cell_data in enumerate(row_data):
            worksheet.write(row_num, col_num, cell_data, unlocked_format)

    workbook.close()

    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = "attachment; filename=part_list.xlsx"

    return response


def export_product(request, fromD, toD, search):
    output = io.BytesIO()
    workbook = Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('party')

    header_format = workbook.add_format({
        'border': 1,
        'bg_color': '#C6EFCE',
        'bold': True,
        'text_wrap': True,
        'valign': 'vcenter',
        'indent': 1,
    })

    headings = ['product_name', 'code', 'desc', 'category', 'purchase_price', 'sale_price', 'present_stock', 'date']
    for col_num, heading in enumerate(headings):
        worksheet.write(0, col_num, heading, header_format)

    unlocked_format = workbook.add_format({'locked': False})
    worksheet.set_column('A:A', 35, unlocked_format)
    worksheet.set_column('B:B', 10, unlocked_format)
    worksheet.set_column('C:C', 25, unlocked_format)
    worksheet.set_column('D:D', 10, unlocked_format)
    worksheet.set_column('E:E', 20, unlocked_format)
    worksheet.set_column('F:F', 20, unlocked_format)
    worksheet.set_column('G:G', 20, unlocked_format)
    worksheet.set_column('H:H', 25, unlocked_format)

    if fromD != 'None':
        pro_data = Product.objects.filter(Q(date__date=fromD))

    if fromD != 'None' and toD != 'None':
        pro_data = Product.objects.filter(Q(date__date__gte=fromD) & Q(date__date__lte=toD))

    if search != 'None':
        pro_data = Product.objects.filter(Q(product_name__iexact=search) |
                                          Q(code__iexact=search) |
                                          Q(category__name__iexact=search) |
                                          Q(present_stock__icontains=search) |
                                          Q(open_stock__icontains=search) |
                                          Q(open_stock__icontains=search) |
                                          Q(purchase_price__icontains=search) |
                                          Q(sale_price__icontains=search)
                                          )

    if fromD == 'None' and toD == 'None' and search == 'None':
        pro_data = Product.objects.all()

    rows = []
    for loop_counter, obj in enumerate(pro_data):
        name = obj.product_name
        code = obj.code
        desc = obj.desc
        cat = str(obj.category)
        p_price = obj.purchase_price
        s_price = obj.sale_price
        o_stock = obj.open_stock
        date = obj.date.strftime("%Y-%m-%d")

        rows.append([name, code, desc, cat, p_price, s_price, o_stock, date])

    for row_num, row_data in enumerate(rows, start=1):
        for col_num, cell_data in enumerate(row_data):
            worksheet.write(row_num, col_num, cell_data, unlocked_format)

    workbook.close()

    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = "attachment; filename=product_list.xlsx"

    return response


def export_trans_hostory(request, fromD, toD, search):
    output = io.BytesIO()
    workbook = Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('party')

    header_format = workbook.add_format({
        'border': 1,
        'bg_color': '#C6EFCE',
        'bold': True,
        'text_wrap': True,
        'valign': 'vcenter',
        'indent': 1,
    })

    headings = ['trans_id', 'product', 'sale_qty', 'base_price', 'discount_type', 'discount', 'net_sale', 'pur_rate',
                'sale_rate', 'open_stock', 'close_stock', 'sale_amt', 'pur_amt', 'date']
    for col_num, heading in enumerate(headings):
        worksheet.write(0, col_num, heading, header_format)

    unlocked_format = workbook.add_format({'locked': False})
    worksheet.set_column('A:A', 15, unlocked_format)
    worksheet.set_column('B:B', 15, unlocked_format)
    worksheet.set_column('C:C', 15, unlocked_format)
    worksheet.set_column('D:D', 15, unlocked_format)
    worksheet.set_column('E:E', 15, unlocked_format)
    worksheet.set_column('F:F', 15, unlocked_format)
    worksheet.set_column('G:G', 15, unlocked_format)
    worksheet.set_column('H:H', 15, unlocked_format)
    worksheet.set_column('I:I', 15, unlocked_format)
    worksheet.set_column('J:J', 15, unlocked_format)
    worksheet.set_column('K:K', 15, unlocked_format)
    worksheet.set_column('L:L', 15, unlocked_format)
    worksheet.set_column('M:M', 15, unlocked_format)
    worksheet.set_column('N:N', 20, unlocked_format)

    if fromD != 'None':
        pro_data = TransactionDetails.objects.filter(Q(date__date=fromD))

    if fromD != 'None' and toD != 'None':
        pro_data = TransactionDetails.objects.filter(Q(date__date__gte=fromD) & Q(date__date__lte=toD))

    if search != 'None':
        pro_data = TransactionDetails.objects.filter(Q(product__product_name__iexact=search) |
                                                     Q(product__category__name__iexact=search) |
                                                     Q(pur_rate__icontains=search) |
                                                     Q(sale_rate__icontains=search) |
                                                     Q(open_stock__icontains=search) |
                                                     Q(close_stock__icontains=search) |
                                                     Q(sale_amt__icontains=search)
                                                     )

    if fromD == 'None' and toD == 'None' and search == 'None':
        pro_data = TransactionDetails.objects.all()

    rows = []
    for loop_counter, obj in enumerate(pro_data):
        trans_id = str(obj.trans_history)
        product = str(obj.product)
        sale_qty = obj.sale_qty
        base_price = obj.base_price
        discount_type = obj.discount_type
        discount = obj.discount
        net_sale = obj.net_sale
        pur_rate = obj.pur_rate
        sale_rate = obj.sale_rate
        open_stock = obj.open_stock
        close_stock = obj.close_stock
        sale_amt = obj.sale_amt
        pur_amt = obj.pur_amt
        date = obj.date.strftime("%Y-%m-%d")

        rows.append([trans_id, product, sale_qty, base_price, discount_type, discount, net_sale, pur_rate, sale_rate,
                     open_stock, close_stock, sale_amt, pur_amt, date])

    for row_num, row_data in enumerate(rows, start=1):
        for col_num, cell_data in enumerate(row_data):
            worksheet.write(row_num, col_num, cell_data, unlocked_format)

    workbook.close()

    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = "attachment; filename=transaction_list.xlsx"

    return response
