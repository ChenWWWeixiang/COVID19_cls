##plot 3cls roc
import seaborn as sns
import os
import csv
import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import sklearn.metrics as metric
from sklearn.calibration import calibration_curve
from sklearn.preprocessing import label_binarize
import pandas as pd
def get_CI(value,res,xx=True):
    sorted_scores=np.array(value)
    sorted_scores.sort()
    confidence_lower = sorted_scores[int(0.05 * len(sorted_scores))]
    confidence_upper = sorted_scores[int(0.95 * len(sorted_scores))]
    if xx:
        res.append(np.mean(value))
    else:
        res.append(str(np.mean(value)) + ' (' + str(confidence_lower) + '-' + str(confidence_upper) + ')')
    return res
import argparse
parser = argparse.ArgumentParser()

parser.add_argument("-i", "--ress", help="A list of npy files which record the performance.",
                    default=['../re/test.npy'])
parser.add_argument("-o", "--output_file", help="Output file path", type=str,
                    default='csvs/results_mc_2.csv')
args = parser.parse_args()

#res=np.load('ipt_results/results/train.npy')
if isinstance(args.ress,str):
    ress=eval(args.ress)
else:
    ress=args.ress
CLS=['Healthy','CAP','A/B Influenza','COVOD-19']
with open(args.output_file,'w') as f:
    f=csv.writer(f)
    f.writerow(['name', 'AUC','Sensitivity','Specificity'])
    for a_res in ress:
        res = np.load(a_res)
        if res.shape[1]==4:
            pre=np.array(res[:,:-1],np.float)
            gt=np.array(res[:,-1],np.float)
        else:
            pre = np.array(res[:, 1:-1], np.float)
            gt = np.array(res[:, -1], np.float)
        #AUC=[]
        ACC=[]
        REC=[]
        SPE=[]
        SAUC=[]
        y_one_hot = label_binarize(gt, np.arange(4))
        norm_x=pre/ pre.max(axis=0)
        for i in range(200):
            train_x, test_x, train_y, test_y = train_test_split(pre, y_one_hot, test_size=0.2)
            train_x=train_x/train_x.max(axis=0)
            #auc = metric.roc_auc_score(train_y, train_x, average='micro')
            #AUC.append(auc)

            prediction = np.argmax(train_x, 1)
            groundtruth = np.argmax(train_y, 1)
            prediction[np.max(train_x[:, 1:], 1) > 0.80] = np.argmax(train_x[np.max(train_x[:, 1:], 1) > 0.80, 1:],
                                                                     1) + 1
            ACC.append(np.mean(prediction == groundtruth))
            sen = []
            spe = []
            sauc = []
            for cls in range(4):
                sen.append(np.sum((prediction == cls) * (groundtruth == cls)) / np.sum(groundtruth == cls))
                spe.append(np.sum((prediction != cls) * (groundtruth != cls)) / np.sum(groundtruth != cls))
                sauc.append(metric.roc_auc_score(train_y[:,cls], train_x[:,cls]))
            SAUC.append(sauc)
            REC.append(sen)
            SPE.append(spe)
        SPE = np.array(SPE)
        REC = np.array(REC)
        SAUC = np.array(SAUC)
        for cls in range(4):
            Res=[CLS[cls]]
            Res = get_CI(SAUC[:, cls], Res)
            Res = get_CI(REC[:, cls], Res)
            Res = get_CI(SPE[:, cls], Res)
            f.writerow(Res)
        plt.figure(1)
        #fpr,tpr,threshold = metric.roc_curve(y_one_hot, norm_x)
        #fpr, tpr, thresholds = metric.roc_curve(y_one_hot.ravel(), norm_x.ravel())
        #plt.plot(fpr, tpr, label='all, AUC={:.2f}'.format(metric.auc(fpr, tpr)))
        fpr, tpr, thresholds = metric.roc_curve(y_one_hot[:,0], norm_x[:,0])
        plt.plot(fpr, tpr, label='healthy, AUC={:.4f}'.format(metric.auc(fpr, tpr)))
        fpr, tpr, thresholds = metric.roc_curve(y_one_hot[:,1], norm_x[:,1])
        plt.plot(fpr, tpr, label='CAP, AUC={:.4f}'.format(metric.auc(fpr, tpr)))
        fpr, tpr, thresholds = metric.roc_curve(y_one_hot[:,2], norm_x[:,2])
        plt.plot(fpr, tpr, label='HXNX, AUC={:.4f}'.format(metric.auc(fpr, tpr)))
        fpr, tpr, thresholds = metric.roc_curve(y_one_hot[:,3], norm_x[:,3])
        plt.plot(fpr, tpr, label='COVID, AUC={:.4f}'.format(metric.auc(fpr, tpr)))
        fps, tps, thresholds=metric.precision_recall_curve(y_one_hot[:,3], norm_x[:,3])
        plt.figure(3)
        plt.plot(fps, tps, label='COVID, AUC={:.4f}'.format(metric.auc(fpr, tpr)))

plt.figure(1)
#plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.0])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic Curve')
plt.legend(loc="lower right")
#plt.show()

plt.savefig('jpgs/roc_4c.jpg')

data=pd.read_csv(args.output_file)
plt.figure(2)
data.plot.bar()
plt.xticks((0,1,2,3),CLS)
plt.title('Metrics for Each Class')
plt.ylabel('Value')
plt.xlabel('Class')
plt.tight_layout()
#plt.xlim([0,4.5])
plt.legend(loc=4)
plt.xticks(rotation=45)
plt.savefig('jpgs/bar_metrics_4c.jpg')
#plt.show()
a=1
plt.figure(3)
plt.title('PR Curve of COVID-19 in Test Cohort')
plt.ylabel('Presicion')
plt.xlabel('Recall')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.0])
plt.tight_layout()
plt.savefig('jpgs/pr_covid.jpg')