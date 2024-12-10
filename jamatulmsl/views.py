from asyncio import log
from collections import OrderedDict
import datetime
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import gatepass
from .serializers import gatepassserializer
from rest_framework import status
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.renderers import TemplateHTMLRenderer
from django.core.exceptions import ObjectDoesNotExist
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import csv
from django.contrib.auth.mixins import LoginRequiredMixin



def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

# from django.template import loader
#  template = loader.get_template('template.html')


from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.contrib.auth.models import User


def forgotpasswordview1(request):
    return render(request, 'forgetpassword.html')

class forgotpasswordview(APIView):
    def get(self, request):
        return render(request, 'forgetpassword.html')



def index(request):
    return render(request, 'index.html')


def signupPage(request):
    if request.method == "POST":
        uname=request.POST.get("Username")
        fname=request.POST.get("Fname")
        lname=request.POST.get("Lname")
        email=request.POST.get("Emailid")
        pass1=request.POST.get("Password")
        pass2=request.POST.get("confirmPassword")

        if pass1 != pass2:
            messages.error(request, "Password doesn't match!")
            return redirect('signup')

        try:
            if User.objects.get(username = uname):
                messages.warning(request, "Username is already taken!")
                return redirect('signup')

        except Exception as identifier:
            pass

        try:
            if User.objects.get(email = email):
                messages.warning(request, "Email ID is already registered!")
                return redirect('signup')

        except Exception as identifier:
            pass

        myuser = User.objects.create_user(uname, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()

        messages.success(request, "SignUp Successful!")
        return render(request, 'login.html')

    return render(request, 'signup.html')

def loginPage(request):

    if request.method == "POST":
        uname=request.POST.get("Username")
        password=request.POST.get("Password")

        myuser = authenticate(username=uname, password=password)

        if myuser is not None:
            login(request, myuser)
            messages.success(request, "Login Successful!")
            return redirect('/')

        else:
            messages.error(request, "Invalid Credentials!")
            return redirect('/login')

    return render(request, 'login.html')


class savepersondetails(LoginRequiredMixin, APIView):
    
    renderer_classes = [TemplateHTMLRenderer]

    login_url = '/login'  # Adjust to your actual login URL

    def handle_no_permission(self):
        messages.error(self.request,  "Login required")
        return super().handle_no_permission()

    def get(self, request):

        idcount = gatepass.objects.all()
        idlst = []
        for i in  idcount.values_list():
            idlst.append(i[0])
        if len(idlst) == 0:
            latestindex = 1
        else:
            latestindex = idlst[-1] + 1

        condata = {
            'ids' : str(latestindex),
        }
        print(condata)

        return render(request, 'registrationform.html', {'context': condata['ids'] })
    
    def post(self, request):
        idcount = gatepass.objects.all()
        idlst = []
        for i in  idcount.values_list():
            idlst.append(i[0])
        if len(idlst) == 0:
            latestindex = 1
        else:
            latestindex = idlst[-1] + 1

        condata = {
            'ids' : str(latestindex),
        }
        print(condata)

        
        if  'button2' in request.POST:
            print('button 2')
            vehicle_no = request.POST.get('vehicle_no1')
            print('vehicle_no', vehicle_no)
            user_profile = gatepass.objects.filter(vehicle_no=vehicle_no).order_by('-date', '-gate_in_time').first()
            form_number =  user_profile.form_number
            user_profile1 = gatepass.objects.filter(form_number=form_number)
            return render(request, "editapplicant1.html", {'user_datas':user_profile1, 'context': condata['ids']}, status=status.HTTP_202_ACCEPTED)
        if 'button1' in request.POST:
            print('button 1')
            serializer = gatepassserializer(data=request.data)
            print(request.data)
            if serializer.is_valid():


                if gatepass.objects.filter(vehicle_no=request.data.get('vehicle_no')).exists():
                    messages.success(request, "Vehicle Number Already Exists")
                    return Response({'error': 'Vehicle Number Already Exists'}, status=400,template_name='registrationform.html')
                elif gatepass.objects.filter(form_number=request.data.get('form_number')).exists():
                    messages.success(request, "Form Number Already Exists")
                    return Response({'error': 'Form Number Already Exists'}, status=400,template_name='registrationform.html')
                gatepass_instance = serializer.save()  # Saves the instance and returns it
                messages.success(request, "Your Applicant has been successfully added!")
                # return Response(serializer.data, status=status.HTTP_201_CREATED)

                form_number =  request.data.get('form_number')
                latestindex = int(form_number) + 1
                
                return render(request, 'registrationform.html', {'context': latestindex }, status=status.HTTP_201_CREATED)
            messages.error(request, "Invalid Entry")
            return Response(serializer.error_messages,status=400, template_name='registrationform.html')


def logoutPage(request):
    logout(request)
    messages.success(request, 'Logout Successful!')
    return redirect('index')

class listResume(LoginRequiredMixin, APIView):

    login_url = '/login'  # Adjust to your actual login URL

    def handle_no_permission(self):
        messages.error(self.request,  "Login required")
        return super().handle_no_permission()

    def get(self, request):

        current_user = request.user.username
        userid = gatepass.USERID

        if gatepass.objects.filter(USERID = current_user).exists():
            profile=gatepass.objects.filter(USERID = current_user)
            return render(request, "listResume.html", {'profile':profile})
        return render(request, 'listResume.html', status=status.HTTP_200_OK)

    def post(self, request):
        current_user = request.user.username
        current_user = request.data.get('Contact_number')
        userid = gatepass.USERID

        if gatepass.objects.filter(userid = current_user).exists():
            profile=gatepass.objects.filter(userid = current_user)
            return render(request, "listResume.html", {'profile':profile})   
        return render(request, "listResume.html", status=status.HTTP_202_ACCEPTED)

class viewResume(LoginRequiredMixin, APIView):

    login_url = '/login'  # Adjust to your actual login URL

    def handle_no_permission(self):
        messages.error(self.request,  "Login required")
        return super().handle_no_permission()

    def post(self, request):
        vehicle_no = request.POST.get('vehicle_no') 
        form_number = request.POST.get('form_number')

        

        # Check if vehicle_no is provided
        if vehicle_no:
            print('vehicle_no:', vehicle_no)
            user_profile = gatepass.objects.filter(vehicle_no=vehicle_no).order_by('-date', '-gate_in_time').first()
            print('user_profile_date', user_profile)
            form_number1 = user_profile.form_number
            print('user_profile_form_number', form_number1)
            user_profile1 = gatepass.objects.filter(form_number=form_number1)
            print('user_profile_form_numberdate', user_profile1)
        else:
            print('form_number:', form_number)
            user_profile1 = gatepass.objects.filter(form_number=form_number)

        if 'button4' in request.POST:
            user_profile = gatepass.objects.filter(form_number=form_number).order_by('-date', '-gate_in_time').first()
            user_profile.delete()
            messages.success(request, 'Deleted Successful!')
            return render(request, 'listResume.html', status=status.HTTP_202_ACCEPTED)
        if  'button2' in request.POST:
            return render(request, "editapplicant.html", {'user_datas':user_profile1}, status=status.HTTP_202_ACCEPTED)
        if  'button5' in request.POST:
            return render(request, "gatepass.html", {'user_datas':user_profile1},status=status.HTTP_202_ACCEPTED)
        return redirect('listResume')

class tally(LoginRequiredMixin, APIView):

    def get(self, request):
        return render(request, 'tallydaterange.html')

    def post(self, request):
        st_dt1 = request.POST.get('startDate')
        ed_dt1 = request.POST.get('endDate')

        current_datet =  datetime.datetime.now()
        current_datedt = current_datet.date()

        user_profile = gatepass.objects.all()
        amountlist = []
        totalvehiclelist = []
        for data in user_profile:
            if data.date is not None:
                dt = datetime.datetime.strptime(str(data.date), '%Y-%m-%d').date()    
            else:
                continue
            if st_dt1 == '' and ed_dt1 == '':
                print('enter date is empty')
                current_datet =  datetime.datetime.now()
                current_datedt = current_datet.date()
                st_dt1 = datetime.datetime.strptime(str(current_datedt), '%Y-%m-%d').date()  # Adjust format if necessary
                ed_dt1 = datetime.datetime.strptime(str(current_datedt), '%Y-%m-%d').date()  # Adjust format if necessary

                if st_dt1 <= dt <= ed_dt1:
                    amountlist.append(int(data.amount))
                    totalvehiclelist.append(str(data.vehicle_no))
                
            else:
                st_dt = datetime.datetime.strptime(str(st_dt1), '%Y-%m-%d').date()  # Adjust format if necessary
                ed_dt = datetime.datetime.strptime(str(ed_dt1), '%Y-%m-%d').date()  # Adjust format if necessary
                if st_dt <= dt <= ed_dt:
                    amountlist.append(int(data.amount))
                    totalvehiclelist.append(str(data.vehicle_no))

        total_sum =  sum(amountlist)
        total_vehicle_count =  len(totalvehiclelist)

        datadict = [{
            'todate': str(st_dt1),
            'fromdate': str(ed_dt1),
            'totlevehicount': str(total_vehicle_count),
            'amtpervehicle': str(20),
            'tottleamt': str(total_sum),
            'currentdate': str(current_datedt)
        }]

        return render(request, "tally.html", {'user_datas': datadict},status=status.HTTP_202_ACCEPTED)
        # return redirect('tallydaterange')
        
 
class exportdata(LoginRequiredMixin, APIView):

    login_url = '/login'  # Adjust to your actual login URL

    def handle_no_permission(self):
        messages.error(self.request,  "Login required")
        return super().handle_no_permission()

    def get(self, request):
        transportersname = gatepass.objects.values_list('transporter_name', flat=True).distinct()
        ImporterTrader = gatepass.objects.values_list('vehicle_owner_name', flat=True).distinct()
        return render(request, 'export.html', {'transporters': transportersname, 'ImporterTrader' : ImporterTrader})

class exporttoexcel(LoginRequiredMixin, APIView):

    login_url = '/login'  # Adjust to your actual login URL

    def handle_no_permission(self):
        messages.error(self.request,  "Login required")
        return super().handle_no_permission()
    
    def post(self,request):
        # try:
        st_dt = request.POST.get('startDate')
        ed_dt = request.POST.get('endDate')
        transporter = request.POST.get('transporter')
        Importer_Trader = request.POST.get('ImporterTrader')
            
        output_json_list = []
        output_json_n = {}
        if st_dt and ed_dt:
            user_profile = gatepass.objects.all() 
        if transporter:
                user_profile = gatepass.objects.filter(transporter_name = transporter)
        if Importer_Trader:
            user_profile = gatepass.objects.filter(vehicle_owner_name = Importer_Trader)
             
        for data in user_profile:
            if data.date is not None:
                dt = datetime.datetime.strptime(str(data.date), '%Y-%m-%d').date()    
            else:
                continue
            if st_dt == '' and ed_dt == '':
                keyList = [
                    'form number',
                    'user id',
                    'transporter name',
                    'driver name',
                    'vehicle owner name',
                    'vehicle no',
                    'date',
                    'gate in time',
                    'driver number',
                    'driver licence no',
                    'amount'
                    ]

                valueList = [
                    str(data.form_number),
                    str(data.USERID),
                    str(data.transporter_name),
                    str(data.driver_name),
                    str(data.vehicle_owner_name),
                    str(data.vehicle_no),
                    str(data.date),
                    str(data.gate_in_time),
                    str(data.driver_number),
                    str(data.driver_licence_no),
                    str(data.amount)
                    ]
                output_json_n = OrderedDict(zip(keyList, valueList))
                output_json_list.append(output_json_n)
            else:
                st_dt = datetime.datetime.strptime(str(st_dt), '%Y-%m-%d').date()  # Adjust format if necessary
                ed_dt = datetime.datetime.strptime(str(ed_dt), '%Y-%m-%d').date()  # Adjust format if necessary
                if st_dt <= dt <= ed_dt:
                    keyList = [
                        'form number',
                        'user id',
                        'transporter name',
                        'driver name',
                        'vehicle owner name',
                        'vehicle no',
                        'date',
                        'gate in time',
                        'driver number',
                        'driver licence no',
                        'amount'
                        ]

                    valueList = [
                        str(data.form_number),
                        str(data.USERID),
                        str(data.transporter_name),
                        str(data.driver_name),
                        str(data.vehicle_owner_name),
                        str(data.vehicle_no),
                        str(data.date),
                        str(data.gate_in_time),
                        str(data.driver_number),
                        str(data.driver_licence_no),
                        str(data.amount)
                        ]
                    output_json_n = OrderedDict(zip(keyList, valueList))
                    output_json_list.append(output_json_n)
        if len(output_json_list) == 0:
            messages.success(request, 'Data Not Found')
            return render(request, 'export.html', status=status.HTTP_404_NOT_FOUND)
    

        filenamedt = datetime.datetime.now()
        now_without_microseconds = filenamedt.replace(microsecond=0)
        file_name = datetime.datetime.strftime(now_without_microseconds, '%Y-%m-%d %H %M %S')
        newfilename = str(file_name) + '.csv'
        fname = f"{newfilename}"
        response = HttpResponse( content_type='text/csv',headers={'Content-Disposition': f'attachment; filename="{fname}"'})
        writer = csv.DictWriter(response, fieldnames=output_json_list[0].keys())
        writer.writeheader()
        for row in output_json_list:
            writer.writerow(row) 
        messages.success(request, 'Data Export Successful!')
        return response
        # except IndexError:
        #     messages.success(request, 'No Data Available in This Range')
        #     return render(request,'export.html' ,status=status.HTTP_400_BAD_REQUEST)

                ## To Download In System CSV File           

                # filenamedt = datetime.datetime.now()
                # now_without_microseconds = filenamedt.replace(microsecond=0)
                # file_name = datetime.datetime.strftime(now_without_microseconds, '%Y-%m-%d %H %M %S')
                # newfilename = str(file_name) + '.csv'
                # with open(str(newfilename), mode='w', newline='') as file:
                #     writer = csv.DictWriter(file, fieldnames=output_json_list[0].keys())
                #     writer.writeheader()
                #     for row in output_json_list:
                #         writer.writerow(row)
                # print(count)
                # print("Data fetched successfully")
                # messages.success(request, 'Data Export Successful Filename ' + str(newfilename))            
                # return Response(output_json_list, status=status.HTTP_200_OK)
    
class updatedetails(LoginRequiredMixin, APIView):

    login_url = '/login'  # Adjust to your actual login URL

    def handle_no_permission(self):
        messages.error(self.request,  "Login required")
        return super().handle_no_permission()

    def post(self, request, vehicle_no, form_number):

        try:
            data  =   gatepass.objects.get(vehicle_no=vehicle_no or form_number)
        except gatepass.DoesNotExist:
            return Response({'error':'Data Not Found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializedata =  gatepassserializer(data, data=request.data, partial=True)
        if serializedata.is_valid():
            serializedata.save()
            messages.success(request, 'Update Successful!' )
            # return Response(serializedata.data)
            return render(request, 'editapplicant.html', status=status.HTTP_200_OK)
        return Response(serializedata.errors, status=status.HTTP_400_BAD_REQUEST)
    

class updateregdetails(LoginRequiredMixin, APIView):

    login_url = '/login'  # Adjust to your actual login URL

    def handle_no_permission(self):
        messages.error(self.request,  "Login required")
        return super().handle_no_permission()

    def post(self, request, vehicle_no):

        # try:
        #     data  =   gatepass.objects.get(vehicle_no=vehicle_no)
        # except gatepass.DoesNotExist:
        #     return Response({'error':'Data Not Found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = gatepassserializer(data=request.data)
        print(request.data)
        
        # serializedata =  gatepassserializer(data, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Vehicle Details Saved Successful!' )
            # return Response(serializedata.data)
            return render(request, 'editapplicant1.html', status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
