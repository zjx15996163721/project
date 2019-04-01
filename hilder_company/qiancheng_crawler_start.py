from company.async_qiancheng import Jobs


if __name__ == '__main__':
    job = Jobs()
    for i in range(0, 10000000, 1000):
        job.get_all_links(i)

