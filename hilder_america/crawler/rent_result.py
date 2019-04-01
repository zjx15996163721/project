from usa_estate import ListedPrice, SoldPrice, RentPrice
import json
import pika
from lib.log import LogHandler

connection = pika.BlockingConnection(pika.ConnectionParameters(host='114.80.150.195', port=5673))
log = LogHandler(__name__)

source = 'realtor'


def rent_consume():
    channel = connection.channel()
    channel.basic_qos(prefetch_count=10)
    channel.basic_consume(callback,
                          queue='rent_result',
                          )
    channel.start_consuming()


def callback(ch, method, properties, body):
    try:
        result = json.loads(body.decode())
        con = json.loads(json.loads(result[0]))
        co_id = result[1]
        info = con['property']
        state = info['state']
        county = info['county']
        city = info['city']
        zipcode = info['postal_code']
        address = info['address']
        try:
            house_type = info['prop_type']
        except:
            house_type = None
        year_built = None
        hoafee = None
        lot_size = None
        agent_name = None
        agent_phone = None
        try:
            property_contact = info['toll_free_number']
        except:
            property_contact = None
        try:
            for room in info['floor_plans']:
                baths = room['baths']
                beds = room['beds']
                room_name = room['name']
                size = room['sqft']
                price = room['price_display']
                available_date = room['available_date']
                r = RentPrice(baths=baths, beds=beds, room_name=room_name,co_id=co_id,
                              size=size, price=price, available_date=available_date,
                              agent_name=agent_name, agent_phone=agent_phone, property_phone=property_contact,
                              state=state, county=county, city=city, zipcode=zipcode,
                              address=address, house_type=house_type, year_built=year_built,
                              hoafee=hoafee, source=source, lot_size=lot_size)
                r.rentprice_insert()
        except:
            baths = info['baths']
            beds = info['beds']
            room_name = None
            size = info['sqft']
            price = info['price_display']
            available_date = None
        r = RentPrice(baths=baths, beds=beds, room_name=room_name,
                      size=size, price=price, available_date=available_date,
                      agent_name=agent_name, agent_phone=agent_phone, property_phone=property_contact,
                      state=state, county=county, city=city, zipcode=zipcode,
                      address=address, house_type=house_type, year_built=year_built,
                      hoafee=hoafee, source=source, lot_size=lot_size)
        r.rentprice_insert()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        log.error(e)
        ch.basic_ack(delivery_tag=method.delivery_tag)

