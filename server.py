#  coding: utf-8 
import socketserver,os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        #print ("Got a request of: %s\n" % self.data.decode())
        allReqDetails = self.data.decode().split()
        reqType = allReqDetails[0]
        reqPath = allReqDetails[1]
        if(reqType != "GET"):# handle all non get reqs
            self.handleIllegal()
            return
        else: # handle all the other get requests
            self.handleRegularResponse(reqPath)
             
            
        
        
    def handleIllegal(self): # if we need to sent 405 for non get meths
        self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n\r\n405 Method Not Allowed",'utf-8'))
        return
    def handleIllegalPath(self): # if we cant find a resource or target
        self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n\r\n404 Not found",'utf-8'))
        return
    def handleSuccess(self, content, mimeType): # send 200 response 
        successResponse = "HTTP/1.1 200 OK\r\nContent-Type: text/" + mimeType+"\r\n\r\n" + content
        #print(successResponse)
        self.request.sendall(bytearray(successResponse,'utf-8'))
        return
    def handleRedirect(self, path): # handling redirection
        print("redirecting")
        newUrl = path + "/"+ "index.html"
        rawNewUrl = (path + "/").replace("./www","") # this is for the respone cause we need to remove root cause its added again
        response = "HTTP/1.1 301 Move Permanently\r\nLocation: " + rawNewUrl + "\r\nContent-Type: text/html\r\n\r\n"

        try:# open file read and add to responses
            resFile=open(newUrl, "r")
            fileCont = resFile.read()
            response += fileCont
            self.request.sendall(bytearray(response,'utf-8'))
            return
        except Exception as e:# handle if file is not found
            print("File is not found " , e )
            self.handleIllegalPath()
            return
    def handleNormal(self,path):# handle normal dir paths when we want just index.html
        newUrl = path + "index.html"
        try:
            resFile = open(newUrl, "r")
            resCont = resFile.read()
            self.handleSuccess(resCont, "html")
            return
        except:
            self.handleIllegalPath()
            return
            
        
    def handleRegularResponse(self,reqPath): # origni points for all reqests
        
        if("../" in reqPath):# Security check
            print("illegal path")
            self.handleIllegalPath()
            return
        
        fileRoot = './www' # root path
        path = fileRoot + reqPath # combine root and path
        #print(reqPath)
        #print(path)
        if(len(reqPath.split(".")) == 2):# If there is file extension(mime specified)
            mimeType = reqPath.split(".")[1]
            print(mimeType)
            #resFile=open(path, "r")
            
            try: # check if they want specific site
                resFile=open(path, "r")
                fileCont = resFile.read()
                self.handleSuccess( fileCont,mimeType)
                return
            except Exception as e:
                print("File is not found " , e )
                self.handleIllegalPath()
                return
        else:# Check directory serve index.html
            # handle redirection
            print("serving index")
            if(path[-1] != "/"):
                self.handleRedirect(path)
                return
            else: # handle serve normal files
                print("serving index regularyly")
                self.handleNormal(path)
                return
            


        
        
        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
