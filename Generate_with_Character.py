
import sys
import os
import pygame
import numpy
import random

import cv2
import datetime

# blocks number and size
blocks = {'1':[0.84,0.84], '2':[0.85,0.43], '4':[0.43,0.43],
          '5':[0.22,0.22], '6':[0.43,0.22], '8':[0.85,0.22],
          '10':[1.68,0.22], '12':[2.06,0.22]}

original_number_blocks = len(blocks)

# blocks number and name
block_names = {'1':"SquareHole", '2':"RectFat", '4':"SquareSmall",
               '5':"SquareTiny", '6':"RectTiny", '8':"RectSmall",
               '10':"RectMedium", '12':"RectBig"}
block_types= {'1':"wood", '2':"ice", '3':"stone"}


wordLength = 0
#目标文字
word = ""
#記録を保存のフォイル
savepath = ""

#评价モード：0：安定だけ  1：平均 2：(A^2+B^2)^0.5
EvaluationMode = 0
#加重平均の時　安定性と類似度の重み
#安定性の重み
StableWeight = 1
#類似度の重み
SimilarWeight = 1

#ブロックの数
quantityOfBlock = 1
#一世代の個体の数
quantityOfSubUnits = 10
#交叉の確率
ProbabilityOfCrossover=0.05
#異変の確率
ProbabilityOfMutation=0.25

#初期データ
stageData = 0
#今回実行の世代のデータ
SubUnits = 0
#今回実行のステージ
targetStage = 0

#パラメータ読み（もしあれば）
def ReadParameters():
    global wordLength,word,savepath
    wordLength = len(sys.argv)
    word = chr(sys.argv[1]) 
    savepath = ""


#文字を画像にする（使っていません）
def DrawTextPicture():
    pygame.init() # now use display and fonts
    font = pygame.font.Font("msgothic.ttc",16)#加载字体与设置大小
    textimg = font.render(word, True, (0, 0, 0), (255, 255, 255))#使用字体绘图

    #检查文件夹并新建
    if (not os.path.exists(os.getcwd()+'/'+savepath)):
        os.makedirs(os.getcwd()+'/'+savepath)

    pygame.image.save(textimg,savepath+'/'+ "word.png")#保存图像

#データ初期化
def datainitialize(startlevel):
    #print("datainitialize")
    global quantityOfBlock,stageData,SubUnits,targetStage
    quantityOfBlock = len(startlevel)
    stageData = numpy.zeros((quantityOfBlock,6))
    SubUnits = numpy.zeros((quantityOfSubUnits,quantityOfBlock,6))
    targetStage = numpy.zeros((quantityOfBlock,6))
    for i in range(quantityOfBlock):
        stageData[i,0] = startlevel[i,0].copy()
        stageData[i,1] = startlevel[i,1].copy()
        stageData[i,2] = startlevel[i,2].copy()
        stageData[i,3] = startlevel[i,3].copy()
        stageData[i,4] = startlevel[i,4].copy()
        stageData[i,5] = startlevel[i,5].copy()
#初始化個体
def initializationSubUnits(inputlevel):
    global SubUnits
    SubUnits = numpy.empty([quantityOfSubUnits,quantityOfBlock,6]) 
    for i in range(quantityOfSubUnits):
        SubUnits[i] = inputlevel.copy()
#実行のステージをコピー
def setTargetStage(level):
    global targetStage
    targetStage = level.copy()

#ステージデータをXMLに書き込む
def wrightlevel(path):
    # write XML
    number_birds=3
    
    f = open(path, "w")
    f.write('<?xml version="1.0" encoding="utf-16"?>\n')
    f.write('<Level width ="2">\n')
    f.write('<Camera x="0" y="2" minWidth="20" maxWidth="30">\n')
    f.write('<Birds>\n')
    for i in range(number_birds):
        f.write('<Bird type="BirdRed"/>\n')
    f.write('</Birds>\n')
    f.write('<Slingshot x="-8" y="-2.5">\n')
    f.write('<GameObjects>\n')

    for i in range(quantityOfBlock):
        a = block_names[str(int(targetStage[i,1]))]
        b = block_types[str(int(targetStage[i,2]))]
        f.write('<Block type="%s" material="%s" x="%s" y="%s" rotation="%s" />\n' % (a,b,str(targetStage[i,3]),str(targetStage[i,4]),str(targetStage[i,5])))

    f.write('</GameObjects>\n')
    f.write('</Level>\n')

    f.close()
#unity启动
def runUnity():
    unitypath = "D:/Desktop/Generate_with_Character/science-birds-master/ScienceBirds.exe"
    os.system(unitypath)

#遺伝的アルゴリズム：
#交叉
def Crossover():
    global SubUnits
    for i in range(quantityOfSubUnits-2):
        for j in range(quantityOfBlock):
            if random.random()<ProbabilityOfCrossover :
                x = SubUnits[i,j]
                SubUnits[i,j] = SubUnits[i+1,j]
                SubUnits[i+1,j] = x
#変異
def Mutation():
    global SubUnits
    for i in range(quantityOfSubUnits-1):
        for j in range(quantityOfBlock):
            if random.random()<ProbabilityOfMutation :
                SubUnits[i,j,3] = SubUnits[i,j,3]+((random.random()-0.5)*0.2)
            if random.random()<ProbabilityOfMutation :
                SubUnits[i,j,4] = SubUnits[i,j,4]+((random.random()-0.5)*0.2)
#評価
def Evaluation():
    #unity実行の結果を読む
    f = open("D:/Desktop/Generate_with_Character/OutPut.txt", "r")
    r = float(f.read())
    r = r / quantityOfBlock
    f.close()
    #類似度を測る
    a = 0
    for i in range(quantityOfBlock):
        a = a+pow(targetStage[i,3]-stageData[i,3],2)+pow(targetStage[i,4]-stageData[i,4],2)
    a = a/quantityOfBlock

    a = a*100
    #if a > 1:
    #    a = 1
    r = r/100
    #if r > 1:
    #    r = 1
    if(EvaluationMode == 0):
        r = r
    elif(EvaluationMode == 1):
        r = (a*SimilarWeight + r*StableWeight)/(StableWeight+SimilarWeight)
    elif(EvaluationMode == 2):
        r = pow(pow(a,2) + pow(r,2),0.5)
    
    #SimilaritylistF.write(str(a)+"\n")

    return r


#---テスト用の初期ステージデータ------------

#quantityOfBlock = 9
#立
stageDataRitsu = [[1,12,3,1.507,-1.962,0],
                [1,8,3,2.043,-2.82,75],
                [1,8,3,1.017,-2.811,105],
                [1,8,3,2.275,-3.403,0],
                [1,8,3,1.517,-1.412,90],
                [1,10,3,1.0337,-3.4189,0],
                [1,10,2,1.542,-2.231,0],
                [1,2,2,2.595,-3.044,0],
                [1,2,2,0.437,-3.038,0]]
stageDataRitsu = numpy.array(stageDataRitsu)
#命
stageDataMei = [[1,12,3,0.84,-1.27,45],
                [1,12,3,2.38,-1.28,-45],
                [1,10,3,1.93,-2.67,90],
                [1,8,3,1.62,-1.36,0],
                [1,8,3,1.11,-1.8,0],
                [1,8,3,0.67,-2.16,90],
                [1,8,3,1.47,-2.18,90],
                [1,8,3,1.09,-2.58,0],
                [1,8,3,2.19,-1.73,0],
                [1,8,3,2.45,-2.18,76],
                [1,10,2,1.58,-1.53,0],
                [1,2,2,0.12,-2.23,90],
                [1,2,2,0.13,-3.08,90],
                [1,2,2,1.07,-3.11,90],
                [1,2,2,2.37,-3.06,90],
                [1,2,2,3.12,-2.26,90],
                [1,2,2,3.12,-3.06,90]]
stageDataMei = numpy.array(stageDataMei)
#館
stageDataKan = [[1,12,3,1.76,-2,90],
                [1,10,3,0.31,-2.25,90],
                [1,10,3,2.32,-0.64,0],
                [1,8,3,0.33,-0.95,45],
                [1,8,3,0.92,-0.77,-45],
                [1,8,3,0.66,-1.3,0],
                [1,8,3,0.82,-2.15,0],
                [1,8,3,0.73,-1.73,45],
                [1,8,3,1.19,-1.65,90],
                [1,8,3,0.81,-2.74,30],
                [1,8,3,2.34,-1.04,0],
                [1,8,3,2.33,-1.97,0],
                [1,8,3,2.31,-2.24,0],
                [1,8,3,2.32,-2.93,0],
                [1,8,3,2.77,-1.49,90],
                [1,8,3,2.83,-2.56,90],
                [1,5,3,0.67,-1.09,0],
                [1,5,3,2.3,-0.41,0],
                [1,10,2,2.34,-0.85,0],
                [1,2,2,0.59,-3.27,0],
                [1,2,2,1.27,-3.06,90],
                [1,2,2,1.93,-3.27,0],
                [1,2,2,2.81,-3.27,0]]
stageDataKan = numpy.array(stageDataKan)
#同
stageDataDou = [[1,12,3,0.78,-2.03,90],
                [1,12,3,2.51,-2.04,90],
                [1,12,3,1.62,-0.9,0],
                [1,8,3,1.65,-1.32,0],
                [1,1,3,1.65,-2.1,0],
                [1,8,2,1.66,-1.5,0],
                [1,2,2,0.59,-3.27,0],
                [1,2,2,1.43,-3.06,90],
                [1,2,2,1.9,-3.06,90],
                [1,2,2,2.59,-3.26,0]]
stageDataDou = numpy.array(stageDataDou)
#志
stageDataShi = [[1,12,3,1.75,-1.27,0],
                [1,10,3,1.75,-1.93,0],
                [1,10,3,2.06,-2.94,0],
                [1,5,3,1.75,-1.7,0],
                [1,5,3,1.75,-1.5,0],
                [1,5,3,1.75,-1.07,0],
                [1,5,3,1.75,-0.88,0],
                [1,8,3,0.53,-2.65,60],
                [1,8,3,1,-2.65,-60],
                [1,8,3,2.03,-2.54,-30],
                [1,8,3,2.92,-2.65,-60],
                [1,12,2,1.75,-2.16,0],
                [1,8,2,1.59,-2.73,0],
                [1,2,2,0.61,-3.27,0],
                [1,2,2,1.46,-3.27,0],
                [1,2,2,2.78,-3.27,0]]
stageDataShi = numpy.array(stageDataShi)
#社
stageDataShya = [[1,12,3,2.12,-2.98,0],
                [1,10,3,2.12,-1.92,0],
                [1,10,3,0.93,-2.69,90],
                [1,5,3,0.92,-1.06,0],
                [1,8,3,2.11,-1.39,90],
                [1,8,3,2.11,-2.45,90],
                [1,8,3,0.9,-1.28,0],
                [1,8,3,0.85,-1.72,-135],
                [1,12,2,1.75,-2.16,90],
                [1,8,2,0.4,-3.27,0],
                [1,2,2,1.41,-3.27,0],
                [1,2,2,2.78,-3.27,0]]
stageDataShya = numpy.array(stageDataShya)
#関
#西
#学
#院
#DrawTextPicture()

#ここを変える============================================================================================
#世代数
LoopTimes = 20
#実行回数
repeatTimes = 1
#初期化
for ret in range(repeatTimes):
    #ここを変える============================================================================================
    word = "馆"
    savepath = "1"

    StableWeight = 1
    SimilarWeight = 5

    EvaluationMode = 1
    datainitialize(stageDataKan)
    #ここを変える============================================================================================

    #個体を初期化
    initializationSubUnits(stageData)
    runTime = 0
    StartTime = datetime.datetime.now()
    LastTime = datetime.datetime.now()

    outputlistF = open("D:/Desktop/Generate_with_Character/List.txt", "w")
    outputlistF.close()
    outputlistF = open("D:/Desktop/Generate_with_Character/List.txt", "a")
    #SimilaritylistF = open("D:/Desktop/Generate_with_Character/SimilarityList.txt", "w")
    #SimilaritylistF.close()
    #SimilaritylistF = open("D:/Desktop/Generate_with_Character/SimilarityList.txt", "a")
    
    LastOutPut = 0
    #フォイルを作る
    SaveTime = str(datetime.datetime.now()).split(".")[0].split(":")
    SaveTime = SaveTime[0]+"-"+SaveTime[1]+"-"+SaveTime[2]
    sp = '/'+SaveTime+" "+word+" mode"+str(EvaluationMode) +" t"+str((ret+1))+"in"+str(repeatTimes)
    #フォイルを検査、なければ作る
    if (not os.path.exists("D:/Desktop/Generate_with_Character"+'/'+sp)):
        os.makedirs("D:/Desktop/Generate_with_Character"+'/'+sp)
    while(1):
        #break
        runTime = runTime + 1
        print('==运行第',runTime,'组==')

        minOutput = 0
        minlevel = 0
        for i in range(quantityOfSubUnits):
            print(i,end='')
            setTargetStage(SubUnits[i])
            wrightlevel("D:/Desktop/Generate_with_Character/level.xml")
            runUnity()
            output = Evaluation()
            if(minOutput == 0 or minOutput>output):
                minOutput = output
                minlevel = i
            #print('  第',runTime,'组第',i+1,'個，評価',output)
        targetStage = SubUnits[minlevel].copy()
        print('')
        print('評価',minOutput)
        initializationSubUnits(targetStage)
        outputlistF.write(str(minOutput)+"\n")
        Crossover()
        Mutation()
        print ('今回掛かった時間',datetime.datetime.now()-LastTime,'全部の時間',datetime.datetime.now()-StartTime)
        
        if(LastOutPut !=0 and minOutput - LastOutPut > 0.15):
            if (not os.path.exists("D:/Desktop/Generate_with_Character"+'/'+sp+'/'+str(runTime))):
                os.makedirs("D:/Desktop/Generate_with_Character"+'/'+sp+'/'+str(runTime))
            wrightlevel("D:/Desktop/Generate_with_Character"+'/'+sp+'/'+str(runTime)+"/level.xml")
        LastOutPut = minOutput

        LastTime = datetime.datetime.now()
        #if(minOutput<0.05):
        #    break
        if(runTime>=LoopTimes):
            break
    outputlistF.close()

    #最终结果を記録
    wrightlevel("D:/Desktop/Generate_with_Character"+'/'+sp+"/level.xml")
    ilistF = open("D:/Desktop/Generate_with_Character/List.txt", "r")
    olistF = open("D:/Desktop/Generate_with_Character"+'/'+sp+"/List.txt", "w")
    for line in ilistF.readlines():
        olistF.write(line)
    ilistF.close()
    olistF.close()

#SimilaritylistF.close()

#scaling_method = int(sys.argv[2])