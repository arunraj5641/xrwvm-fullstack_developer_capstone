import React, { useState, useEffect } from 'react';
import "./Dealers.css";
import "../assets/style.css";
import Header from '../Header/Header';
import review_icon from "../assets/reviewicon.png";

const Dealers = () => {
  const [dealersList, setDealersList] = useState([]);
  const [states, setStates] = useState([]);

  const filterDealers = async (state) => {
    const url = state === "All"
      ? "/djangoapp/get_dealers"
      : "/djangoapp/get_dealers/" + encodeURIComponent(state);
    const res = await fetch(url);
    const data = await res.json();
    if (data.status === 200) setDealersList(data.dealers);
  };

  const getDealers = async () => {
    const res = await fetch("/djangoapp/get_dealers");
    const data = await res.json();
    if (data.status === 200) {
      setDealersList(data.dealers);
      setStates([...new Set(data.dealers.map(dealer => dealer.state))]);
    }
  };

  useEffect(() => { getDealers(); }, []);

  const username = sessionStorage.getItem("username");
  const isLoggedIn = username !== null;

  return (
    <div>
      <Header />
      {isLoggedIn && <p style={{margin: "8px 16px"}}>Logged in as: {username}</p>}
      <table className="table">
        <thead>
          <tr>
            <th>ID</th><th>Dealer Name</th><th>City</th>
            <th>Address</th><th>Zip</th>
            <th>
              <select name="state" id="state"
                defaultValue="" onChange={e => filterDealers(e.target.value)}>
                <option value="" disabled>State</option>
                <option value="All">All States</option>
                {states.map(state => <option key={state} value={state}>{state}</option>)}
              </select>
            </th>
            {isLoggedIn && <th>Review Dealer</th>}
          </tr>
        </thead>
        <tbody>
          {dealersList.map(dealer => (
            <tr key={dealer.id}>
              <td>{dealer.id}</td>
              <td><a href={`/dealer/${dealer.id}`}>{dealer.full_name}</a></td>
              <td>{dealer.city}</td>
              <td>{dealer.address}</td>
              <td>{dealer.zip}</td>
              <td>{dealer.state}</td>
              {isLoggedIn && (
                <td>
                  <a href={`/postreview/${dealer.id}`}>
                    <img src={review_icon} className="review_icon" alt="Post Review" />
                  </a>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Dealers;
