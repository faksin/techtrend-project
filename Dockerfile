#use python base image
FROM python:3.8

#set working directory
WORKDIR /app

#copy all the dependecies files
ADD techtrends/ . 

#set label
ARG BUILD_DATE
LABEL org.label-schema.build-date==$BUILD_DATE

#install and run dependencies
RUN pip install -r requirements.txt
RUN python init_db.py

#expose the port 3111
EXPOSE 3111

#start the container
CMD ["python", "app.py"]