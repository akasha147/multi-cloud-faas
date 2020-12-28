def insert_photographer(event,context):
    
    triggerCloud = multicloud.getTriggerCloud()
    targetCloud = multicloud.getTargetCloud()

    database = multicloud.handlers.noSqlDatabaseHandler(cloudName = triggerCloud)
    insert_response = database.insert(TableName="photographers",Item=event)
    return insert_response

def insert_product(event,context):
    
    triggerCloud = multicloud.getTriggerCloud()
    targetCloud = multicloud.getTargetCloud()

    database = multicloud.handlers.noSqlDatabaseHandler(cloudName = triggerCloud)
    insert_response = database.insert(TableName="catalog",Item=event)
    return insert_response

def assign_photographer_to_product(event,context):
    triggerCloud = multicloud.getTriggerCloud()
    targetCloud = multicloud.getTargetCloud()
    

    trigger_details = multicloud.triggers.Trigger(cloudName = triggerCloud,triggerType="no-sql-database",event=event)
    
    if trigger_details.eventName == "INSERT":
        
        database = multicloud.handlers.noSqlDatabaseHandler(cloudName = triggerCloud)
        photographers = database.get_all(TableName="photographers")
        assigned_id = photographers[random.randint(0,len(photographers)-1)]['ID']
        product_id = trigger_details.item['ID']

        assignment_tuple = {
            'timestamp':time.ctime(time.time()),
            'product-id':product_id,
            'photographer-id':assigned_id
        }

        insert_response = database.insert(TableName="assignment",Item=assignment_tuple)
        return insert_response     
        



