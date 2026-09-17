# MODELLED occupancy cost per city: typical (not prime) high-street retail rent and office rent,
# in local currency per m2 per year. Calibration anchors: Cushman & Wakefield "Main Streets Across
# the World 2025" prime-street rents (digital report, fetched 13 Sep 2026); typical street modelled
# at ~8-15% of prime, cross-checked against city market reports. Every figure is MODELLED - the
# site's Method tab says so and tells users to get agent quotes. office = office prime typical.
# city: (retail_typical, office_typical, note)
RENTS = {
 'paris':(850,550,'prime CE ~12k+ EUR/sqm/yr'), 'lyon':(320,290,''), 'marseille':(260,240,''),
 'toulouse':(220,230,''), 'bordeaux':(240,250,''), 'lille':(200,220,''), 'nice':(260,240,'Croisette anchor 6,075 prime'),
 'nantes':(190,210,''), 'strasbourg':(200,210,''),
 'madrid':(420,360,'prime Preciados ~3k'), 'barcelona':(380,330,''), 'valencia':(180,190,''),
 'seville':(170,180,''), 'bilbao':(190,200,''), 'malaga':(160,170,''), 'zaragoza':(150,160,''),
 'berlin':(340,420,'Ku-damm prime ~3.5k'), 'munich':(380,480,'Kaufinger prime ~3.7k'),
 'hamburg':(300,340,''), 'cologne':(260,280,'Schildergasse prime ~3k'), 'frankfurt':(280,400,'Zeil prime ~3k'),
 'stuttgart':(250,290,''), 'dusseldorf':(270,320,''), 'leipzig':(160,170,''),
 'rome':(380,350,'Via del Corso anchor ~6k prime'), 'milan':(520,650,'Montenapoleone ~16-20k prime'),
 'naples':(220,200,''), 'turin':(200,210,''), 'florence':(280,280,'Via Roma anchor 6,000 prime'), 'bologna':(210,230,''),
 'amsterdam':(420,450,'Kalverstraat prime ~3k'), 'rotterdam':(240,260,''), 'the-hague':(210,230,''),
 'utrecht':(230,250,''), 'brussels':(330,320,''), 'antwerp':(260,250,''),
 'vienna':(340,300,'Kaerntner Strasse prime ~4k'), 'zurich':(650,700,'Bahnhofstrasse prime ~9k CHF'),
 'geneva':(420,450,''),
 'prague':(380,280,'Na Prikope prime ~2.6k EUR-equiv'), 'budapest':(260,240,''),
 'warsaw':(300,290,''), 'krakow':(220,190,''),
 'lisbon':(280,250,'Chiado prime ~1.7k'), 'porto':(190,180,''),
 'stockholm':(420,500,'Biblioteksgatan prime ~1k EUR-equiv... modelled'), 'gothenburg':(220,240,''),
 'copenhagen':(380,340,'Stroeget prime'), 'helsinki':(280,290,''), 'oslo':(360,420,''),
 'athens':(240,200,'Ermou prime ~2.9k'), 'bucharest':(200,190,''),
 'zagreb':(180,160,''), 'bratislava':(160,150,''), 'ljubljana':(150,140,''), 'sofia':(140,120,''),
 'dublin':(360,600,'Grafton prime ~6k'), 'tallinn':(150,150,''), 'riga':(130,120,''), 'vilnius':(140,130,''),
 'luxembourg':(320,480,''), 'valletta':(170,190,''),
}
