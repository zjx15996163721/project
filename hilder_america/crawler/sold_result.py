from usa_estate import ListedPrice, SoldPrice, RentPrice
import json
import pika
from lib.log import LogHandler

connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.195', port=5673))
log = LogHandler(__name__)

source = 'realtor'


def sold_consume():
    channel = connection.channel()
    channel.basic_qos(prefetch_count=10)
    channel.basic_consume(callback,
                          queue='sold_result',
                          )
    channel.start_consuming()


def callback(ch, method, properties, body):
    try:
        result = json.loads(body.decode())
        con = json.loads(json.loads(result[0]))
        co_id = result[1]
        info = con['property']
        beds = info['beds']
        baths = info['baths']
        state = info['state']
        county = info['county']
        city = info['city']
        zipcode = info['postal_code']
        address = info['address']
        size = info['sqft']
        year_built = info['year_built']
        price = info['price']
        avg_price = info['price_per_sqft_display']
        lot_size = info['lot_size']
        try:
            agent_name = info['listing_provider']['agent_name']
            agent_phone = info['listing_provider']['office_contact']
        except:
            agent_name = None
            agent_phone = None
        try:
            house_type = info['prop_type']
        except:
            house_type = None
        sold_date = info['sold_date']
        try:
            hoafee = info['hoa_fee']
        except:
            hoafee = None
        s = SoldPrice(source=source,co_id=co_id,
                      city=city, beds=beds, baths=baths, state=state, county=county,
                      zipcode=zipcode, address=address, house_type=house_type, lot_size=lot_size,
                      size=size, year_built=year_built, hoafee=hoafee, price=price,
                      avg_price=avg_price, deal_date=sold_date, agent_name=agent_name, agent_phone=agent_phone,
                      )
        s.soldprice_insert()
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        log.error(e)
        ch.basic_ack(delivery_tag=method.delivery_tag)


