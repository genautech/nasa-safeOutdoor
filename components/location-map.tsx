'use client';

import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix Leaflet default marker icon
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

function MapUpdater({ center }: { center: [number, number] }) {
  const map = useMap();
  
  useEffect(() => {
    map.setView(center, 13);
  }, [center, map]);
  
  return null;
}

function MapClickHandler({ onMapClick }: { onMapClick?: (lat: number, lon: number) => void }) {
  useMapEvents({
    click(e) {
      if (onMapClick) {
        onMapClick(e.latlng.lat, e.latlng.lng);
      }
    },
  });
  return null;
}

interface LocationMapProps {
  lat: number;
  lon: number;
  locationName: string;
  onMapClick?: (lat: number, lon: number) => void;
}

export function LocationMap({ lat, lon, locationName, onMapClick }: LocationMapProps) {
  return (
    <div className="w-full h-full rounded-lg overflow-hidden border shadow-md">
      <MapContainer
        center={[lat, lon]}
        zoom={13}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker position={[lat, lon]} key={`${lat}-${lon}`}>
          <Popup>
            <div className="text-sm">
              <p className="font-semibold">{locationName}</p>
              <p className="text-xs text-muted-foreground">
                {lat.toFixed(4)}, {lon.toFixed(4)}
              </p>
            </div>
          </Popup>
        </Marker>
        <MapUpdater center={[lat, lon]} />
        <MapClickHandler onMapClick={onMapClick} />
      </MapContainer>
    </div>
  );
}
