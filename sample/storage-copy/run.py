def copy(event,context):

    triggerCloud = multicloud.getTriggerCloud()
    targetCloud = multicloud.getTargetCloud()

    storage = multicloud.handlers.StorageHandler(cloudName = triggerCloud,event=event)
    trigger = multicloud.triggers.Trigger(cloudName = targetCloud,triggerType="storage",event=event)
    
    output_bucket = "outgoing-traffic"

    copyResponse = storage.copyObject(Bucket=trigger.BucketName,CopySource = trigger.BucketName+"/"+trigger.Key,Key = "copy_"+trigger.Key)
    return copyResponse
        