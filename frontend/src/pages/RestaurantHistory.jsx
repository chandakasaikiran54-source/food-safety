import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { QRCodeSVG } from 'qrcode.react';
import api from '../utils/api';

const RestaurantHistory = () => {
  const [searchParams] = useSearchParams();
  const name = searchParams.get('name');
  const location = searchParams.get('location');
  
  const [restaurant, setRestaurant] = useState(null);
  const [inspections, setInspections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [notVisited, setNotVisited] = useState(false);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const searchRes = await api.get(`/restaurants/search?name=${encodeURIComponent(name)}&location=${encodeURIComponent(location)}`);
        if (searchRes.data.success) {
          const res = await api.get(`/restaurants/${searchRes.data.data._id}`);
          setRestaurant(res.data.data.restaurant);
          setInspections(res.data.data.inspections);
          if (!res.data.data.inspections || res.data.data.inspections.length === 0) {
            setNotVisited(true);
          }
        }
      } catch (err) {
        if (err.response?.status === 404) {
          setNotVisited(true);
        } else {
          console.error("Error fetching restaurant:", err);
        }
      }
      setLoading(false);
    };

    if (name && location) {
      fetchHistory();
    } else {
      setLoading(false);
    }
  }, [name, location]);

  if (loading) return <div className="text-center mt-8">Loading inspection history...</div>;

  return (
    <div className="animate-fade-in" style={{ padding: '40px 5%', maxWidth: '800px', margin: '0 auto' }}>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '2rem', marginBottom: '8px' }}>{name}</h2>
          <p style={{ color: '#cbd5e1', fontSize: '1.1rem' }}>{location}</p>
        </div>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          {restaurant && (
            <Link to={`/complaints/new?restaurantId=${restaurant._id}&restaurantName=${encodeURIComponent(restaurant.name)}`} className="btn btn-primary" style={{ background: 'var(--warning-color)', color: '#000', border: 'none' }}>
              Report Issue
            </Link>
          )}
          <Link to="/restaurants/search" className="btn btn-secondary">Back to Search</Link>
        </div>
      </div>

      {notVisited ? (
        <div className="glass-card text-center" style={{ padding: '60px 20px', border: '1px solid var(--warning-color)', background: 'rgba(234, 179, 8, 0.1)' }}>
          <h2 style={{ color: 'var(--warning-color)', marginBottom: '16px', fontSize: '2rem' }}>NOT VISITED</h2>
          <p style={{ color: '#cbd5e1', fontSize: '1.2rem', marginBottom: '8px' }}>No food inspection record found for this restaurant.</p>
          <p style={{ color: '#94a3b8' }}>Please do not assume the restaurant is safe simply because there is no record.</p>
        </div>
      ) : (
        <>
          <div className="glass-card mb-8" style={{ borderLeft: `6px solid ${restaurant?.latestInspectionStatus === 'Safe' ? 'var(--score-excellent)' : 'var(--score-high-concern)'}`}}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap' }}>
              <div>
                <h3 style={{ marginBottom: '8px' }}>Current Inspection Status</h3>
                <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: restaurant?.latestInspectionStatus === 'Safe' ? 'var(--score-excellent)' : 'var(--warning-color)' }}>
                  {restaurant?.latestInspectionStatus}
                </p>
              </div>
              {restaurant && (
                <div style={{ textAlign: 'center', background: '#fff', padding: '8px', borderRadius: '8px' }}>
                  <QRCodeSVG value={`${window.location.origin}/restaurants/history?name=${encodeURIComponent(restaurant.name)}&location=${encodeURIComponent(restaurant.location)}`} size={80} />
                  <p style={{ color: '#000', fontSize: '0.7rem', marginTop: '4px', fontWeight: 'bold' }}>Scan to Verify</p>
                </div>
              )}
            </div>
          </div>

          <h3 className="mb-4">Inspection History</h3>
          
          {inspections.length === 0 ? (
            <p>No inspections found.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {inspections.map((insp, index) => (
                <div key={insp._id} className="glass-card" style={{ padding: '24px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--glass-border)', paddingBottom: '12px', marginBottom: '16px' }}>
                    <h4 style={{ fontSize: '1.2rem' }}>Inspection {inspections.length - index}</h4>
                    <span style={{ color: '#cbd5e1' }}>Date: {new Date(insp.date).toLocaleDateString()}</span>
                  </div>
                  
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    <div>
                      <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Food Status</p>
                      <p style={{ fontWeight: 'bold' }}>{insp.foodStatus}</p>
                    </div>
                    <div>
                      <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Hygiene Rating</p>
                      <p style={{ fontWeight: 'bold' }}>{insp.hygieneRating}/5</p>
                    </div>
                    <div>
                      <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Raw Materials</p>
                      <p style={{ fontWeight: 'bold' }}>{insp.rawMaterialStatus}</p>
                    </div>
                    <div>
                      <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Kitchen Cleanliness</p>
                      <p style={{ fontWeight: 'bold' }}>{insp.kitchenCleanliness}</p>
                    </div>
                    <div>
                      <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Food Storage</p>
                      <p style={{ fontWeight: 'bold' }}>{insp.foodStorageCondition}</p>
                    </div>
                    <div>
                      <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Waste Management</p>
                      <p style={{ fontWeight: 'bold' }}>{insp.wasteManagement}</p>
                    </div>
                    <div>
                      <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Pest Control</p>
                      <p style={{ fontWeight: 'bold' }}>{insp.pestControl}</p>
                    </div>
                    <div>
                      <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Staff Hygiene</p>
                      <p style={{ fontWeight: 'bold' }}>{insp.staffHygiene}</p>
                    </div>
                    <div style={{ gridColumn: '1 / -1', background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px', display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#cbd5e1' }}>Overall Rating</span>
                      <span style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{insp.overallRating}/5</span>
                    </div>
                    <div style={{ gridColumn: '1 / -1' }}>
                      <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Inspector</p>
                      <p>{insp.officerId?.name}</p>
                    </div>
                    {insp.remarks && (
                      <div style={{ gridColumn: '1 / -1' }}>
                        <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Remarks</p>
                        <p style={{ fontStyle: 'italic' }}>"{insp.remarks}"</p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default RestaurantHistory;
