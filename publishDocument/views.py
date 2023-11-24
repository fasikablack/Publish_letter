from django.shortcuts import render
import xmlrpc.client
from datetime import datetime 
from io import BytesIO
import calendar
import os
from pdf2image import convert_from_path
from pdf2jpg import pdf2jpg
import pypdfium2 as pdfium
import cv2
# install pillow
from PIL import Image
from django.http import HttpResponse
import time

def main(request):
    db = 'realestate_db'
    username = 'fasikazelalem12@gmail.com'
    password = '123'
    customers = ""
    document_type = ['Warning','Cancellation']
    # common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    common = xmlrpc.client.ServerProxy('http://192.168.10.31:8069/xmlrpc/2/common')    
    uid = common.authenticate(db,username,password,{})
    if uid:
        # models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        models = xmlrpc.client.ServerProxy('http://192.168.10.31:8069/xmlrpc/2/object')
        customers = models.execute_kw(db,uid,password,'res.partner','search_read',[[]],{'fields':['name']})
        # print(customers)
    # for a in user:
    #     print(a['name'])
    if request.GET.get('customer'):
        print(str(request.GET.get('customer')))
        print(request.GET.get('Date'))
        print(request.GET.get('documentType'))

        _, _, files = next(os.walk("/home/atcom/Documents/Project_Realestate/Publish_Document/publish_document/publishDocument/static/letterFiles/templates/"+str(request.GET.get('documentType'))+"/"))
        file_count = len(files)
        # print(request.GET.get('referenceNum'))
        for pageNum in range(file_count):
            if str(request.GET.get('documentType')) == 'Cancellation':
                if pageNum == 0:
                    top_left_x,top_left_y,bottom_right_x,bottom_right_y = 288,572,576,611
                    editContractFile(top_left_x,top_left_y,bottom_right_x,bottom_right_y,pageNum,str(request.GET.get('customer')),str(request.GET.get('documentType')))

                    top_left_x,top_left_y,bottom_right_x,bottom_right_y = 256,366,601,401
                    editContractFile(top_left_x,top_left_y,bottom_right_x,bottom_right_y,pageNum,str(request.GET.get('Date')),str(request.GET.get('documentType')))

                    top_left_x,top_left_y,bottom_right_x,bottom_right_y = 312,443,642,479
                    editContractFile(top_left_x,top_left_y,bottom_right_x,bottom_right_y,pageNum,str(request.GET.get('referenceNum')),str(request.GET.get('documentType')))
            if str(request.GET.get('documentType')) == 'Warning':
                if pageNum == 0:
                    top_left_x,top_left_y,bottom_right_x,bottom_right_y = 226,689,525,722
                    editContractFile(top_left_x,top_left_y,bottom_right_x,bottom_right_y,pageNum,str(request.GET.get('customer')),str(request.GET.get('documentType')))

                    top_left_x,top_left_y,bottom_right_x,bottom_right_y = 255,485,634,517
                    editContractFile(top_left_x,top_left_y,bottom_right_x,bottom_right_y,pageNum,str(request.GET.get('Date')),str(request.GET.get('documentType')))

                    top_left_x,top_left_y,bottom_right_x,bottom_right_y = 313,563,675,599
                    editContractFile(top_left_x,top_left_y,bottom_right_x,bottom_right_y,pageNum,str(request.GET.get('referenceNum')),str(request.GET.get('documentType')))

        Images_list = []
        for a in range(file_count):
            Images_list.append(str(a)+".jpg")

        images = [
        Image.open("/home/atcom/Documents/Project_Realestate/Publish_Document/publish_document/publishDocument/static/letterFiles/Modified_IMG/"+str(request.GET.get('documentType'))+"/" + f)
        for f in Images_list
        ]

        # pdf_path = "/home/atcom/Documents/Project_Realestate/Publish_Document/publish_document/publishDocument/static/letterFiles/letterPDF/CancelationLetter.pdf"

        # images[0].save(
        # pdf_path, "PDF" ,resolution=100.0, save_all=True, append_images=images[1:]
        # )

        buffer = BytesIO()

        try:
            images[0].save(buffer, "PDF", resolution=100.0, save_all=True, append_images=images[1:])
        except Exception as e:
            return HttpResponse("error")

        # Set the buffer's file pointer to the beginning
        buffer.seek(0)

        # Create a response with the appropriate content type and headers
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="your_filename.pdf"'
        response.write(buffer.read())

        return response
    
    return render(request,"api/Publish_document.html",{'customers':customers,'document_type':document_type})

def editContractFile(top_left_x,top_left_y,bottom_right_x,bottom_right_y,pageNum,replaceWord,documentType):
    file_path = '/home/atcom/Documents/Project_Realestate/Publish_Document/publish_document/publishDocument/static/letterFiles/Modified_IMG/'+str(documentType)+'/'+str(pageNum)+'.jpg'
    file_path_new = '/home/atcom/Documents/Project_Realestate/Publish_Document/publish_document/publishDocument/static/letterFiles/templates/'+str(documentType)+'/'+str(pageNum)+'.jpg'
    if os.path.exists(file_path):
        img = cv2.imread(file_path)
    else:
        img = cv2.imread(file_path_new)

    x, y, width, height = top_left_x, top_left_y, (bottom_right_x - top_left_x), (bottom_right_y - top_left_y)
    
    # Create a white rectangle to cover the desired portion of the image
    white = (255, 255, 255)
    img[y:y + height, x:x + width] = white
    
    # Write text on the white rectangle using a white color
    font = cv2.FONT_HERSHEY_COMPLEX
    org = (x , y + int(height / 1.5))
    fontScale = 1
    color = (0, 0, 0)
    thickness = 2
    text = replaceWord
    img = cv2.putText(img, text, org, font, fontScale, color, thickness, cv2.LINE_AA)
    
    # Save the resulting image
    cv2.imwrite('/home/atcom/Documents/Project_Realestate/Publish_Document/publish_document/publishDocument/static/letterFiles/Modified_IMG/'+str(documentType)+'/'+str(pageNum)+'.jpg', img)
    # return 'yes'
