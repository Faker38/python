fp=open('note.txt','w')#打开文件
print('北京',file=fp)  #将北京欢迎你写到note文件中
fp.close() #关闭文件