import os
import random
from faker import Faker
from faker.providers import internet
import pandas as pd


def read_inputs(source=None):
    """Read in inputs from text source"""
    with open(source, 'r') as f:
        data = f.readlines()
    data = [x.replace('\n', '') for x in data]
    return data


def main():
    """Main workflow"""
    fake = Faker()
    fake.add_provider(internet)

    # Get positive and negative reviews
    total_reviews = read_inputs(source='./setup-files/reviews.txt')
    random.shuffle(total_reviews)

    for i in range(100):

        # Schema: name, address, IP address, review
        name, address, ip_address, review = [], [], [], []

        for _ in range(100):
            name.append(fake.name())
            fake_address = fake.address()
            fake_address = fake_address.replace('\n', ' ')
            address.append(fake_address)
            ip_address.append(fake.ipv4_private())
            review.append(random.choice(total_reviews))

        # Create dataframe of results
        fake_data = {
                "name": name,
                "address": address,
                "IPV4": ip_address,
                "customer_review": review,
                }
        df = pd.DataFrame(fake_data)

        # Create directory if it does not exist
        datapath = './generated-data/'
        if not os.path.exists(datapath):
            os.makedirs('./generated-data/')

        df.to_parquet(datapath + '/' + 'sample_data' + str(i) + '.parquet', index=False)  # encoding='utf-8')


if __name__ == "__main__":
    main()
