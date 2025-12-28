import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import "./Dealers.css";
import "../assets/style.css";
import positive_icon from "../assets/positive.png";
import neutral_icon from "../assets/neutral.png";
import negative_icon from "../assets/negative.png";
import review_icon from "../assets/reviewbutton.png";
import Header from '../Header/Header';

const Dealer = () => {
  const [dealer, setDealer] = useState({});
  const [reviews, setReviews] = useState([]);
  const [unreviewed, setUnreviewed] = useState(false);

  const { id } = useParams();
  const BASE_URL = window.location.origin;

  const dealer_url = `${BASE_URL}/djangoapp/dealer/${id}`;
  const reviews_url = `${BASE_URL}/djangoapp/reviews/dealer/${id}`;
  const post_review_url = `/postreview/${id}`;

  const get_dealer = async () => {
    const res = await fetch(dealer_url, {
      method: "GET"
    });
    const retobj = await res.json();

    if (retobj.status === 200) {
      const dealerobjs = Array.from(retobj.dealer);
      setDealer(dealerobjs[0]);
    }
  };

  const get_reviews = async () => {
    const res = await fetch(reviews_url, {
      method: "GET"
    });
    const retobj = await res.json();

    if (retobj.status === 200) {
      if (retobj.reviews.length > 0) {
        setReviews(retobj.reviews);
      } else {
        setUnreviewed(true);
      }
    }
  };

  const senti_icon = (sentiment) => {
    if (sentiment === "positive") return positive_icon;
    if (sentiment === "negative") return negative_icon;
    return neutral_icon;
  };

  useEffect(() => {
    get_dealer();
    get_reviews();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const isLoggedIn = Boolean(sessionStorage.getItem("username"));

  return (
    <div style={{ margin: "20px" }}>
      <Header />
      <div style={{ marginTop: "10px" }}>
        <h1 style={{ color: "grey" }}>
          {dealer.full_name}
          {isLoggedIn && (
            <a href={post_review_url}>
              <img
                src={review_icon}
                style={{ width: '10%', marginLeft: '10px', marginTop: '10px' }}
                alt='Post Review'
              />
            </a>
          )}
        </h1>
        <h4 style={{ color: "grey" }}>
          {dealer['city']},{dealer['address']}, Zip - {dealer['zip']}, {dealer['state']}
        </h4>
      </div>
      <div className="reviews_panel">
        {reviews.length === 0 && unreviewed === false ? (
          <p>Loading Reviews....</p>
        ) : unreviewed === true ? (
          <div>No reviews yet!</div>
        ) : (
          reviews.map((review, index) => (
            <div className='review_panel' key={index}>
              <img
                src={senti_icon(review.sentiment)}
                className="emotion_icon"
                alt='Sentiment'
              />
              <div className='review'>{review.review}</div>
              <div className="reviewer">
                {review.name} {review.car_make} {review.car_model} {review.car_year}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Dealer;
