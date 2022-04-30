from django.shortcuts import render
from django.http import HttpResponse

from .forms import fileform
#########
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
############
# Create your views here.
from plotly.offline import plot
from plotly.graph_objs import Scatter
import csv
from django.core.files.storage import FileSystemStorage


 ##########################################DATA ANALYSIS PART########################

def ecg_analysis(url1, url2):
	#data normalization
	df = pd.read_csv("C:/Users/HO/Desktop/s6/project/Ecg_dj/"+str(url1))
	df['V5'] = (df['V5'] -df['V5'].mean())/abs(df['V5']).max()
	df['MLII'] = (df['V5'] -df['MLII'].mean())/abs(df['MLII']).max()
	#data filtering

	import scipy.io.wavfile
	import scipy.signal
	# read ECG data from the WAV file
	#sampleRate, data = scipy.io.wavfile.read('ecg.wav')
	sampleRate=360
	times = np.arange(len(df["V5"]))/sampleRate
	# apply a 3-pole lowpass filter at 0.1x Nyquist frequency
	b, a = scipy.signal.butter(3, 0.1)
	df["V5"] = scipy.signal.filtfilt(b, a, df["V5"])
	df["MLII"] = scipy.signal.filtfilt(b, a, df["MLII"])
	#################
	Rpeaks = pd.read_csv("C:/Users/HO/Desktop/s6/project/Ecg_dj/"+str(url2))
	
	#Feature extraction
	##RR interval
	Rpeaks["RR_interval"] = np.nan
	for i in range(1,len(Rpeaks)):
	    start= Rpeaks['Rpeaks'][i]
	    end= Rpeaks['Rpeaks'][i-1]
	    Rpeaks['RR_interval'][i]=start-end
	#pre-RR
	Rpeaks["pre_RR"] = np.nan
	for i in range(2,len(Rpeaks)):
	    start= Rpeaks['Rpeaks'][i-1]
	    end= Rpeaks['Rpeaks'][i-2]
	    Rpeaks['pre_RR'][i]=start-end
	#post-RR
	Rpeaks["post_RR"] = np.nan
	for i in range(0,len(Rpeaks)-1):
	    start= Rpeaks['Rpeaks'][i+1]
	    end= Rpeaks['Rpeaks'][i]
	    Rpeaks['post_RR'][i]=start-end
    
	#Diference between RR and pre-RR intervals
	Rpeaks['RR_preRR']=Rpeaks['RR_interval']-Rpeaks['pre_RR'] 
	#Diference between post-RR and RR intervals
	Rpeaks['postRR_RR']=Rpeaks['post_RR']-Rpeaks['RR_interval']
	############################################################
	Rpeaks["inter_min"] = np.nan
	Rpeaks["inter_max"] = np.nan
	for i in range(2,len(Rpeaks)-2):
	    b= Rpeaks['Rpeaks'][i]
	    a= Rpeaks['Rpeaks'][i-1]
	    #[c1,c2] represent the heartbeat interval  
	    c1=b-int(abs(0.3*(b-a)))
	    c2=int(abs(0.6*(a-b)))+b
	    Rpeaks['inter_min'][i]=c1
	    Rpeaks['inter_max'][i]=c2
	QRS = []
	#Ts=360
	#QRS=Pj -(Ts/10) 
	a=36
	b=36
	s= df['V5']
	for i in range(2, len(Rpeaks)-1):
	    
	    QRS.append(s[(Rpeaks['Rpeaks'][i]-a):(Rpeaks['Rpeaks'][i]+b)])
	x6=[]
	x7=[]
	x8=[]
	for i in range(len(QRS)-1):
	    x6.append(pow(QRS[i],2).sum())  # QRS complex energy
	    x7.append(abs(QRS[i].max()/QRS[i].where(lambda x: x != 0).min())) #QRS complex polarity
	    x8.append(QRS[i].var())  #QRS Variance

	x6 = np.array(x6)
	x7 = np.array(x7)
	x8 = np.array(x8)
	#Ts=360
	#QRS=Pj -(Ts/10) 
	a=36
	b=36
	Rpeaks["QRS_min"] = np.nan
	Rpeaks["QRS_max"] = np.nan

	for i in range(2, len(Rpeaks)-1):
	    Rpeaks["QRS_min"][i]=Rpeaks['Rpeaks'][i]-a
	    Rpeaks["QRS_max"][i]=Rpeaks['Rpeaks'][i]+b

	Rpeaks["polarity"] = np.nan
	Rpeaks["energy"] = np.nan
	Rpeaks["variance"] = np.nan

	for i in range(2, len(Rpeaks)-2):
	    Rpeaks["energy"][i]=x6[i-2]
	    Rpeaks["polarity"][i]=x7[i-2]
	    Rpeaks["variance"][i]=x8[i-2]
    #################################################################
    #################################################################
    #################################################################
    #################################################################
	#data ploting
	ax = plt.axes(projection='3d')
	# Data for a three-dimensional line
	zdata = Rpeaks["RR_interval"][0:1000]
	xdata = Rpeaks["Rpeaks"][0:1000]
	ydata = Rpeaks["post_RR"][0:1000]
	ax.set_title('');
	ax.set_xlabel('Rpeaks')
	ax.set_ylabel('post_RR')
	ax.set_zlabel('RR_interval');
	ax.scatter3D(xdata, ydata, zdata);
	plt.savefig("C:/Users/HO/Desktop/s6/project/Ecg_dj/static/plot.png")
	plt.close()

	plt.scatter(list(range(0,1000)), Rpeaks['Rpeaks'][0:1000])
	plt.title('Rpeaks distribution')
	plt.savefig("C:/Users/HO/Desktop/s6/project/Ecg_dj/static/Rpeaks.png")
	plt.close()

	plt.hist(Rpeaks['type'])
	plt.title("type")
	plt.savefig("C:/Users/HO/Desktop/s6/project/Ecg_dj/static/type.png")
	plt.close()

	plt.scatter(list(range(0,1000)), Rpeaks['sampling_rate'][0:1000])
	plt.title("sampling rate distribution")
	plt.savefig("C:/Users/HO/Desktop/s6/project/Ecg_dj/static/sampling_rate.png")
	plt.close()

	plt.scatter(list(range(0,1000)), Rpeaks['RR_interval'][0:1000])
	plt.title("RR_interval distribution")
	plt.savefig("C:/Users/HO/Desktop/s6/project/Ecg_dj/static/RR_interval.png")
	plt.close()

	plt.scatter(list(range(0,1000)), Rpeaks['pre_RR'][0:1000])
	plt.title("pre_RR distribution")
	plt.savefig("C:/Users/HO/Desktop/s6/project/Ecg_dj/static/pre_RR.png")
	plt.close()

	plt.scatter(list(range(0,1000)), Rpeaks['post_RR'][0:1000])
	plt.title("post_RR distribution")
	plt.savefig("C:/Users/HO/Desktop/s6/project/Ecg_dj/static/post_RR.png")
	plt.close()

	plt.scatter(list(range(0,1000)), Rpeaks['RR_preRR'][0:1000])
	plt.title("RR_preRR distribution")
	plt.savefig("C:/Users/HO/Desktop/s6/project/Ecg_dj/static/RR_preRR.png")
	plt.close()
	return 1


###################################################################################33

def home(request):
	return render(request, 'home.html')

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def result(request):
    request_file1 = request.FILES['data']
    request_file2 = request.FILES['rpeaks']
    if request_file1 and request_file2:
        fs = FileSystemStorage()
        file1 = fs.save(request_file1.name, request_file1)
        file2 = fs.save(request_file2.name, request_file2)
        fileurl1 = fs.url(file1)
        fileurl2 = fs.url(file2)
    res = ecg_analysis(fileurl1, fileurl2)
    return render(request, "result.html")


def result1(request):
	return render(request, "result.html")



