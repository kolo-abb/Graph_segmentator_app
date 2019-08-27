import os
import sqlite3

from Graph_Segmentator.settings import BASE_DIR


def save_mst(img_base,img_segmented,name,description,edges,threshold,const,min_size,threshold2=None,
             const2=None,min_size2=None,max_size2=999999999,counter=0):
    if const2 is None:
        const2=const
    if min_size2 is None:
        min_size2=min_size
    if threshold2 is None:
        threshold2=threshold
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'db.sqlite3'))
    cur = conn.cursor()
    cur.execute('INSERT INTO MST_Segmentation (Edges, Threshold,Const,Min_size,Threshold_2,Min_size_2,'
                ' Max_size_2,Const_2, Counter ) VALUES (?, ?,?,?,?,?,?,?,?);',(edges,threshold,const, min_size,threshold2,
                                                                   min_size2,max_size2,const2,counter))

    cur.execute('select last_insert_rowid();')
    id=cur.fetchall()

    cur.execute('INSERT INTO Segmentations (Name, Description, Base_image, Segmented_image, Method,Parameters) '
                'VALUES (?, ?,?,?,?,?);',(name,description,img_base, img_segmented,'MST_Segmentation',id[0][0]))
    conn.commit()

    conn.close()

def save_ngc(img_base,img_segmented,name,description,type,sensivity,sensivity_location,counter=0):

    conn = sqlite3.connect(os.path.join(BASE_DIR, 'db.sqlite3'))
    cur = conn.cursor()
    cur.execute('INSERT INTO NGC_Segmentation (Type, Sensivity, Sensivity_location, Counter)'
                ' VALUES (?, ?,?, ?);',(type,sensivity,sensivity_location,counter))

    cur.execute('select last_insert_rowid();')
    id=cur.fetchall()

    cur.execute('INSERT INTO Segmentations (Name, Description, Base_image, Segmented_image, Method,Parameters) '
                'VALUES (?, ?,?,?,?,?);',(name,description,img_base, img_segmented,'NGC_Segmentation',id[0][0]))
    conn.commit()

    conn.close()

def save_two_cc(img_base,img_segmented,name,description,channel,threshold,filling,const,counter=0):

    conn = sqlite3.connect(os.path.join(BASE_DIR, 'db.sqlite3'))
    cur = conn.cursor()
    cur.execute('INSERT INTO Two_cc_Segmentation (Channel, Threshold, Filling, Const, Counter)'
                ' VALUES (?, ?,?,?,?);',(channel,threshold,filling,const,counter))

    cur.execute('select last_insert_rowid();')
    id=cur.fetchall()

    cur.execute('INSERT INTO Segmentations (Name, Description, Base_image, Segmented_image, Method,Parameters) '
                'VALUES (?, ?,?,?,?,?);',(name,description,img_base, img_segmented,'Two_cc_Segmentation',id[0][0]))
    conn.commit()

    conn.close()

def save_interactive(img_base,img_segmented,name,description,counter=0):
    return None

