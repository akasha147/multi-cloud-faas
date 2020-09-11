const {
  App,
  StorageMiddleware,
  HTTPBindingMiddleware,
} = require("@multicloud/sls-core");

const { 
  AwsModule,
  SimpleStorageMiddleware
} = require("@multicloud/sls-aws");


const app = new App(new AwsModule());
const options = {
  container: "multi-cloud-storage",
  path: "uploads/image.png"
};

const handler = context => {
  const { req } = context;
  const name = req.query.get("name");
  const result = context.storage.read(options);
  console.log(result)
  context.send("hello",200);
};


const handler1 = context => {
    console.log(context.event)
};

module.exports.readS3 = app.use(
  [
    HTTPBindingMiddleware(),
    StorageMiddleware(),
    SimpleStorageMiddleWare()
  ],
  handler
);

module.exports.uploadS3 = app.use([StorageMiddleware(),SimpleStorageMiddleware()],handler1);