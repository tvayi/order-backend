var conn = new Mongo();
var db = conn.getDB("myDB");

// Creating order collection
db.createCollection("order", {
    validator: {$jsonSchema: {
        bsonType: "object",
        required: ["code", "created_at"],
        properties: {
            code: {
                bsonType: "string",
            },
            created_at: {
                bsonType: "string",
            }
        }
    }}
});
db.order.createIndex({ "code": 1 });


// Creating ProductItem collection
db.createCollection("productItem", {
    validator: {$jsonSchema: {
        bsonType: "object",
        required: ["product_code", "order_code", "name", "amount", "price"],
        properties: {
            product_code: {
                bsonType: "string",
            },
            order_code: {
                bsonType: "string",
            },
            name: {
                bsonType: "string",
            },
            amount: {
                bsonType: "int",
            },
            price: {
                bsonType: "double",
            }
        }
    }}
});
db.productItem.createIndex({ "product_code": 1});
