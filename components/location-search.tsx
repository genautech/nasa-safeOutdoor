'use client';

import { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { MapPin, Search, Loader2 } from 'lucide-react';

interface Location {
  name: string;
  displayName: string;
  lat: number;
  lon: number;
  type: string;
}

interface LocationSearchProps {
  onLocationSelect: (location: Location) => void;
  defaultValue?: string;
}

export function LocationSearch({ onLocationSelect, defaultValue }: LocationSearchProps) {
  const [query, setQuery] = useState(defaultValue || '');
  const [results, setResults] = useState<Location[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    const searchTimer = setTimeout(() => {
      if (query.length >= 3) {
        searchLocations(query);
      } else {
        setResults([]);
      }
    }, 500); // Debounce 500ms

    return () => clearTimeout(searchTimer);
  }, [query]);

  const searchLocations = async (searchQuery: string) => {
    setIsSearching(true);
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?` +
        `format=json&q=${encodeURIComponent(searchQuery)}&limit=8&addressdetails=1`,
        {
          headers: {
            'Accept': 'application/json',
            'User-Agent': 'SafeOutdoor/1.0'
          }
        }
      );

      const data = await response.json();
      
      const locations: Location[] = data.map((item: any) => ({
        name: item.name || item.address?.city || item.address?.town || 'Unknown',
        displayName: item.display_name,
        lat: parseFloat(item.lat),
        lon: parseFloat(item.lon),
        type: item.type
      }));

      setResults(locations);
      setShowResults(true);
    } catch (error) {
      console.error('Location search error:', error);
      setResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSelect = (location: Location) => {
    setQuery(location.displayName);
    setShowResults(false);
    onLocationSelect(location);
  };

  return (
    <div className="relative w-full">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          type="text"
          placeholder="Search any location worldwide..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setShowResults(true)}
          className="pl-10 pr-10"
        />
        {isSearching && (
          <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin text-muted-foreground" />
        )}
      </div>

      {showResults && results.length > 0 && (
        <div className="absolute z-[9999] w-full mt-2 bg-white dark:bg-gray-800 border rounded-lg shadow-xl max-h-[300px] overflow-y-auto">
          <div className="p-2 space-y-1" onClick={(e) => e.stopPropagation()}>
            {results.map((location, index) => (
              <button
                key={index}
                onClick={() => handleSelect(location)}
                className="w-full text-left p-3 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <div className="flex items-start gap-2">
                  <MapPin className="h-4 w-4 mt-0.5 text-muted-foreground flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{location.name}</p>
                    <p className="text-xs text-muted-foreground truncate">
                      {location.displayName}
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {query.length >= 3 && results.length === 0 && !isSearching && (
        <p className="text-xs text-muted-foreground mt-2">No locations found</p>
      )}
    </div>
  );
}
