import csv
from datetime import datetime
from io import BytesIO
from django.core.mail import EmailMessage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import get_template
from party.models import Party
from product.models import Product, TransactionHistory, TransactionDetails
from xhtml2pdf import pisa
import os




def convert_date(date_string, output_format='%Y-%m-%d'):
    date_object = datetime.strptime(date_string, '%Y-%m-%d')
    formatted_date = date_object.strftime(output_format)
    return formatted_date


def generateBILL(request):
    if request.method == 'POST':
        form = request.POST
        party = form.get('party')
        bill_date = form.get('bill_date')
        bill_date = convert_date(bill_date)
        product_id = form.getlist('product_id')
        sale_qty = form.getlist('sale_qty')
        closeStock = form.getlist('closeStock')
        price = form.getlist('price')
        type_discount = form.getlist('type_discount')
        discount = form.getlist('discount')
        discount_price = form.getlist('discount_price')
        subtotal = form.getlist('subtotal')
        cash_credit = form.get('cash_type')

        trans_id = TransactionHistory.objects.create(invoice_number=str(datetime.now().strftime("%H%M%S")),
                                                     party_id=party,
                                                     cash_credit=cash_credit,
                                                     date=bill_date)

        if trans_id:
            for i in range(len(product_id)):
                product_data = Product.objects.get(id=product_id[i])
                open_stock = int(product_data.open_stock)
                present_stock = product_data.present_stock - int(sale_qty[i])
                pur_rate = int(product_data.purchase_price)
                sale_price = int(product_data.sale_price)
                sale_amt = int(sale_qty[i]) * sale_price
                # pur_amt = int(sale_qty[i]) * pur_rate
                pur_amt = present_stock * pur_rate

                TransactionDetails.objects.create(trans_history_id=trans_id.id,
                                                  product_id=product_id[i],
                                                  sale_qty=sale_qty[i],
                                                  base_price=price[i],
                                                  discount_type=type_discount[i],
                                                  discount=discount[i],
                                                  discount_price=discount_price[i],
                                                  net_sale=subtotal[i],
                                                  pur_rate=pur_rate,
                                                  sale_rate=sale_price,
                                                  open_stock=open_stock,
                                                  close_stock=present_stock,
                                                  sale_amt=sale_amt,
                                                  pur_amt=pur_amt,
                                                  date=bill_date,
                                                  )

                Product.objects.filter(id=product_id[i]).update(present_stock=present_stock)
            return redirect(f'/view-invoice/{trans_id.id}/')
    else:
        party = Party.objects.all()
        context = {'party': party, }
        return render(request, 'generateBILL.html', context)


def view_invoice(request, id=None):
    if id is not None:
        invoice_detail = TransactionHistory.objects.get(id=id)
        party = invoice_detail.party
        party_add = invoice_detail.party.address
        party_contact = invoice_detail.party.phone_no
        cash_credit = invoice_detail.cash_credit
        invoice_no = invoice_detail.invoice_number
        invoice_date = invoice_detail.date
        invoice = TransactionDetails.objects.filter(trans_history_id=id)
        data_list = []
        total_price = 0
        for i in invoice:
            data_dict = {}
            data_dict['invoice'] = i.trans_history.invoice_number
            data_dict['code'] = i.product.code
            data_dict['product_name'] = i.product.product_name
            data_dict['sale_qty'] = i.sale_qty
            data_dict['base_price'] = i.base_price
            data_dict['discount_type'] = i.discount_type
            data_dict['discount'] = i.discount_price
            data_dict['net_sale'] = i.net_sale
            data_dict['sale_rate'] = i.sale_rate
            data_dict['sale_amt'] = i.sale_amt
            data_dict['date'] = i.date
            data_dict['party'] = i.trans_history.party
            total_price += data_dict['net_sale']

            data_list.append(data_dict)
        context = {
            'bill_id': id,
            'cash_credit': cash_credit,
            'party': party,
            'party_add': party_add,
            'party_contact': party_contact,
            'invoice_no': invoice_no,
            'invoice_date': invoice_date,
            'data_list': data_list,
            'invoice': invoice,
            'total_price': total_price,
        }
        return render(request, 'invoice_view.html', context)
    else:
        invoice = TransactionHistory.objects.all().order_by('-id')[:25]
        context = {
            'invoice': invoice,
        }
        return render(request, 'invoice_template.html', context)


def edit_bill(request, bill_id):
    if request.method == 'POST':
        form = request.POST
        bill_id = form.get('bill_id')
        party = form.get('party')
        bill_date = form.get('bill_date')
        bill_date = convert_date(bill_date)
        product_id = form.getlist('product_id')
        sale_qty = form.getlist('sale_qty')
        closeStock = form.getlist('closeStock')
        price = form.getlist('price')
        type_discount = form.getlist('type_discount')
        discount = form.getlist('discount')
        discount_price = form.getlist('discount_price')
        print(discount_price,'--------------------------discount_price')
        subtotal = form.getlist('subtotal')
        cash_credit = form.get('cash_type')

        trans_id = TransactionHistory.objects.filter(id=bill_id).update(
            invoice_number=str(datetime.now().strftime("%H%M%S")),
            party_id=party,
            cash_credit=cash_credit,
            date=bill_date)

        detail = TransactionDetails.objects.filter(trans_history_id=bill_id)
        for i in detail:
            qty = Product.objects.get(id=i.product.id)
            qty = int(qty.present_stock) + int(i.sale_qty)
            Product.objects.filter(id=i.product.id).update(present_stock=qty)

        TransactionDetails.objects.filter(trans_history_id=bill_id).delete()

        if trans_id:
            for i in range(len(product_id)):
                product_data = Product.objects.get(id=product_id[i])
                open_stock = int(product_data.open_stock)
                present_stock = product_data.present_stock - int(sale_qty[i])
                pur_rate = int(product_data.purchase_price)
                sale_price = int(product_data.sale_price)
                sale_amt = int(sale_qty[i]) * sale_price
                pur_amt = present_stock * pur_rate

                TransactionDetails.objects.create(trans_history_id=bill_id,
                                                  product_id=product_id[i],
                                                  sale_qty=sale_qty[i],
                                                  base_price=price[i],
                                                  discount_type=type_discount[i],
                                                  discount=discount[i],
                                                  discount_price=discount_price[i],
                                                  net_sale=subtotal[i],
                                                  pur_rate=pur_rate,
                                                  sale_rate=sale_price,
                                                  open_stock=open_stock,
                                                  close_stock=present_stock,
                                                  sale_amt=sale_amt,
                                                  pur_amt=pur_amt,
                                                  date=bill_date,
                                                  )

                Product.objects.filter(id=product_id[i]).update(present_stock=present_stock)
            return redirect(f'/view-invoice/{bill_id}/')

    else:
        trans_detail = TransactionHistory.objects.get(id=bill_id)
        date = trans_detail.date
        cash_credit = trans_detail.cash_credit
        party_details = trans_detail.party

        items_detail = TransactionDetails.objects.filter(trans_history_id=bill_id)
        context = {
            'bill_id': bill_id,
            'date': date,
            'cash_credit': cash_credit,
            'party_details': party_details,
            'items_detail': items_detail,
        }
        return render(request, 'edit_bill.html', context)


def transactionHISTORY(request):
    transaction = TransactionDetails.objects.all()

    context = {
        'transaction': transaction
    }
    return render(request, 'transHISTORY.html', context)


def export_data_to_csv(request, param):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data.csv"'

    writer = csv.writer(response)
    if param == 'transaction':
        writer.writerow([field.name for field in TransactionDetails._meta.fields])  # Write field names as CSV header

        data = TransactionDetails.objects.all()

        for item in data:
            row_data = [str(getattr(item, field.name)) for field in TransactionDetails._meta.fields]
            writer.writerow(row_data)

    elif param == 'party':
        writer.writerow([field.name for field in Party._meta.fields])  # Write field names as CSV header

        data = Party.objects.all()

        for item in data:
            row_data = [str(getattr(item, field.name)) for field in Party._meta.fields]
            writer.writerow(row_data)

    elif param == 'product':
        writer.writerow([field.name for field in Product._meta.fields])  # Write field names as CSV header

        data = Product.objects.all()

        for item in data:
            row_data = [str(getattr(item, field.name)) for field in Product._meta.fields]
            writer.writerow(row_data)

    return response


def get_user(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        party = Party.objects.get(id=id)

        json_data = {
            'name': party.customer_name if party.customer_name else '',
            'address': party.address if party.address else '',
            'contact': party.phone_no if party.phone_no else '',
            'email': party.email if party.email else '',
            'pincode': party.pipcode if party.pipcode else '',
        }
        return JsonResponse(json_data)


# def generate_pdf(request, id):
#     template_src = 'render_pdf.html'
#     pass
#     if id is not None:
#         invoice_detail = TransactionHistory.objects.get(id=id)
#         party = invoice_detail.party
#         party_add = invoice_detail.party.address
#         cash_credit = invoice_detail.cash_credit
#         invoice_no = invoice_detail.invoice_number
#         invoice_date = invoice_detail.date
#         invoice = TransactionDetails.objects.filter(trans_history_id=id)
#         data_list = []
#         total_price = 0
#         for i in invoice:
#             data_dict = {}
#             data_dict['invoice'] = i.trans_history.invoice_number
#             data_dict['code'] = i.product.code
#             data_dict['product_name'] = i.product.product_name
#             data_dict['sale_qty'] = i.sale_qty
#             data_dict['base_price'] = i.base_price
#             data_dict['discount_type'] = i.discount_type
#             data_dict['discount'] = i.discount
#             data_dict['net_sale'] = i.net_sale
#             data_dict['sale_rate'] = i.sale_rate
#             data_dict['sale_amt'] = i.sale_amt
#             data_dict['date'] = i.date
#             data_dict['party'] = i.trans_history.party
#             total_price += data_dict['net_sale']
#
#             data_list.append(data_dict)
#
#         context = {
#             'bill_id': id,
#             'cash_credit': cash_credit,
#             'party': party,
#             'party_add': party_add,
#             'invoice_no': invoice_no,
#             'invoice_date': invoice_date,
#             'data_list': data_list,
#             'invoice': invoice,
#             'total_price': total_price,
#         }
#
#         template = get_template(template_src)
#         html = template.render(context)
#         result = BytesIO()
#         pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
#         if pdf.err:
#             return HttpResponse("Invalid PDF", status_code=400, content_type='text/plain')
#         return HttpResponse(result.getvalue(), content_type='application/pdf')


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def generate_pdf(request, id):
    if id is not None:
        invoice_detail = TransactionHistory.objects.get(id=id)
        party = invoice_detail.party
        party_add = invoice_detail.party.address
        party_name = invoice_detail.party.customer_name
        cash_credit = invoice_detail.cash_credit
        invoice_no = invoice_detail.invoice_number
        invoice_date = invoice_detail.date
        invoice = TransactionDetails.objects.filter(trans_history_id=id)
        data_list = []
        total_price = 0
        for i in invoice:
            data_dict = {}
            data_dict['invoice'] = i.trans_history.invoice_number
            data_dict['code'] = i.product.code
            data_dict['product_name'] = i.product.product_name
            data_dict['sale_qty'] = i.sale_qty
            data_dict['base_price'] = i.base_price
            data_dict['discount_type'] = i.discount_type
            data_dict['discount'] = i.discount
            data_dict['net_sale'] = i.net_sale
            data_dict['sale_rate'] = i.sale_rate
            data_dict['sale_amt'] = i.sale_amt
            data_dict['date'] = i.date
            data_dict['party'] = i.trans_history.party
            total_price += data_dict['net_sale']

            data_list.append(data_dict)

        context = {
            'bill_id': id,
            'cash_credit': cash_credit,
            'party': party,
            'party_add': party_add,
            'recipient_name': party_name,
            'invoice_no': invoice_no,
            'invoice_date': invoice_date,
            'data_list': data_list,
            'invoice': invoice,
            'total_price': total_price,
        }
    pdf = render_to_pdf('render_pdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "your_Bill.pdf"  # Change the filename accordingly
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    return HttpResponse("Error generating PDF")


# def send_pd_whatsapp(pary_contact, subject, recipient_list):
#     subject = subject + ' please check your email '+ recipient_list
#     try:
#         c_time = datetime.now().strftime("%H")
#         pywhatkit.sendwhatmsg_instantly(f'+91{pary_contact}', subject, c_time)
#     except:
#         pass
        
def send_email(request, id):
    invoice_detail = TransactionHistory.objects.get(id=id)
    party = invoice_detail.party
    recipient_list = invoice_detail.party.email
    pary_contact = str(invoice_detail.party.phone_no)
    message = f"HELLO, {invoice_detail.party.customer_name}"
    subject = 'Your Bill Generated'
    from_email = 'info@sanjay.solutions'
    # Generate the PDF using the PDF view
    pdf_response = generate_pdf(request, id)
    if pdf_response:
        pdf_content = pdf_response.content

        # Create an EmailMessage instance
        email = EmailMessage(subject, message, from_email, [recipient_list])
        email.attach("your_pdf_filename.pdf", pdf_content, 'application/pdf')  # Attach the PDF

        try:
            email.send()
            # send_pd_whatsapp(pary_contact, subject, recipient_list)
            # send_whatsapp_message('hello geeta')
            return HttpResponse("Email sent successfully")
        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}")
    else:
        return HttpResponse("Error generating PDF")

def cash_credit_party(request, status):
    obj = TransactionHistory.objects.filter(cash_credit=status)
    page_status = status
    context = {
        'credit_obj': obj,
        'page_status': page_status,
    }
    return render(request,'cash_credit.html', context)

def party_payment_status(request, status, trans_id):
    if status == 'Credit':
        TransactionHistory.objects.filter(id=trans_id).update(cash_credit='Cash')
        return redirect(f'/credit-party/{status}/')
    else:
        TransactionHistory.objects.filter(id=trans_id).update(cash_credit='Credit')
        return redirect(f'/cash-party/{status}/')

