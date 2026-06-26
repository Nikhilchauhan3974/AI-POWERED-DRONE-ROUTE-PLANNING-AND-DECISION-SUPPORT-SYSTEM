# Bounding boxes represent [lat_min, lon_min], [lat_max, lon_max]
LOCATIONS = {
    "USA": {
        "California": {
            "Los Angeles": {
                "Santa Monica": {
                    "center": {"lat": 34.0194, "lon": -118.4912},
                    "bounds": {"min_lat": 33.995, "min_lon": -118.520, "max_lat": 34.040, "max_lon": -118.460}
                }
            }
        },
        "New York": {
            "New York City": {
                "Manhattan Central": {
                    "center": {"lat": 40.7831, "lon": -73.9712},
                    "bounds": {"min_lat": 40.760, "min_lon": -73.990, "max_lat": 40.805, "max_lon": -73.950}
                }
            }
        }
    },
    "India": {
        "Maharashtra": {
            "Mumbai": {
                "Bandra Kurla": {
                    "center": {"lat": 19.060, "lon": 72.860},
                    "bounds": {"min_lat": 19.040, "min_lon": 72.830, "max_lat": 19.080, "max_lon": 72.890}
                }
            },
            "Pune": {
                "Shivaji Nagar": {
                    "center": {"lat": 18.5308, "lon": 73.8475},
                    "bounds": {"min_lat": 18.510, "min_lon": 73.820, "max_lat": 18.550, "max_lon": 73.870}
                }
            }
        },
        "Karnataka": {
            "Bengaluru": {
                "Indiranagar Sector": {
                    "center": {"lat": 12.9719, "lon": 77.6412},
                    "bounds": {"min_lat": 12.950, "min_lon": 77.610, "max_lat": 12.990, "max_lon": 77.670}
                }
            }
        },
        "Delhi NCT": {
            "Delhi": {
                "Connaught Place": {
                    "center": {"lat": 28.6304, "lon": 77.2177},
                    "bounds": {"min_lat": 28.610, "min_lon": 77.190, "max_lat": 28.650, "max_lon": 77.240}
                }
            }
        },
        "Tamil Nadu": {
            "Chennai": {
                "Nungambakkam": {
                    "center": {"lat": 13.0604, "lon": 80.2496},
                    "bounds": {"min_lat": 13.040, "min_lon": 80.220, "max_lat": 13.080, "max_lon": 80.270}
                }
            }
        },
        "West Bengal": {
            "Kolkata": {
                "Salt Lake": {
                    "center": {"lat": 22.5804, "lon": 88.4179},
                    "bounds": {"min_lat": 22.560, "min_lon": 88.390, "max_lat": 22.600, "max_lon": 88.440}
                }
            }
        },
        "Telangana": {
            "Hyderabad": {
                "Gachibowli": {
                    "center": {"lat": 17.4483, "lon": 78.3488},
                    "bounds": {"min_lat": 17.425, "min_lon": 78.320, "max_lat": 17.470, "max_lon": 78.370}
                }
            }
        },
        "Gujarat": {
            "Ahmedabad": {
                "Satellite Area": {
                    "center": {"lat": 23.0300, "lon": 72.5180},
                    "bounds": {"min_lat": 23.010, "min_lon": 72.490, "max_lat": 23.050, "max_lon": 72.540}
                }
            }
        },
        "Rajasthan": {
            "Jaipur": {
                "C Scheme Sector": {
                    "center": {"lat": 26.9124, "lon": 75.8038},
                    "bounds": {"min_lat": 26.890, "min_lon": 75.770, "max_lat": 26.930, "max_lon": 75.830}
                }
            }
        },
        "Uttar Pradesh": {
            "Lucknow": {
                "Hazratganj Crossing": {
                    "center": {"lat": 26.8500, "lon": 80.9400},
                    "bounds": {"min_lat": 26.830, "min_lon": 80.910, "max_lat": 26.870, "max_lon": 80.960}
                }
            }
        },
        "Uttar Pradesh West": {
            "Indore District": {
                "Vijay Nagar Center": {
                    "center": {"lat": 22.7533, "lon": 75.8937},
                    "bounds": {"min_lat": 22.730, "min_lon": 75.860, "max_lat": 22.770, "max_lon": 75.920}
                }
            }
        }
    },
    "UAE": {
        "Dubai": {
            "Dubai Metro": {
                "Downtown Dubai": {
                    "center": {"lat": 25.2048, "lon": 55.2708},
                    "bounds": {"min_lat": 25.185, "min_lon": 55.240, "max_lat": 25.225, "max_lon": 55.300}
                }
            }
        }
    },
    "Germany": {
        "Berlin State": {
            "Berlin District": {
                "Berlin Mitte": {
                    "center": {"lat": 52.5200, "lon": 13.4050},
                    "bounds": {"min_lat": 52.500, "min_lon": 13.370, "max_lat": 52.540, "max_lon": 13.440}
                }
            }
        }
    }
}
