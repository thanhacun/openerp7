def round_base(x, base=5):
        return int(base * round(float(x)/base))
    
def get_new_from_tree( cr, uid, id, object, lists, field, startnum=1, step_num=1, context={}):
    res = 0
    list_delete=[]
    #list_new_update=[]
    list_nochange=[]
    list_delete = [0]
    lists_remain = []
    for lst in lists:
        if lst[0] in (2,3,5): #Delete Cut Link
            list_delete.append(lst[1])
        elif lst[0]==4:
            list_nochange.append(lst[1])
        elif lst[0]==1:
            if field not in lst[2]:
                list_nochange.append(lst[1])
            else:
                lists_remain.append(lst)
        else:
            lists_remain.append(lst)
            
    max_sq=startnum - step_num
    for lst in lists_remain:
        if max_sq<lst[2][field]:
            max_sq = lst[2][field]
    if id:
        object_name = object.__class__.__name__
        try:
            table_name = object._table_name
        except:
            table_name = object_name.replace('.','_')
        res_ids = False
        if list_nochange:
            res_ids = ",".join(map(str,list_nochange))
        
        except_ids = ",".join(map(str,list_delete))
        
        if res_ids:
            cr.execute("""Select max(%s) from %s where id not in (%s) and id in (%s)""" % (field,table_name,except_ids,res_ids))
            exist_max_val = cr.fetchone()[0]
        else:
            exist_max_val = 0
        
        if max_sq<exist_max_val:
            max_sq = exist_max_val
    res = max_sq+step_num
    return res