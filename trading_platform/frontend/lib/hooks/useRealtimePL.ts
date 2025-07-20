import { useEffect, useRef } from 'react';

interface RealtimePLMessage {
  clientId: string;
  pnl: number;
}

interface UseRealtimePLOptions {
  onMessage?: (data: RealtimePLMessage) => void;
}

const useRealtimePL = ({ onMessage }: UseRealtimePLOptions = {}) => {
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Ensure WebSocket is only created once
    if (!ws.current) {
      ws.current = new WebSocket('ws://localhost:8000/ws/pl');

      ws.current.onopen = () => {
        console.log('WebSocket connection established for P/L data.');
      };

      ws.current.onmessage = (event) => {
        try {
          const data: RealtimePLMessage = JSON.parse(event.data);
          onMessage?.(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.current.onclose = () => {
        console.log('WebSocket connection closed for P/L data.');
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    }

    return () => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.close();
        ws.current = null; // Clear the ref
      }
    };
  }, [onMessage]);

  return ws.current;
};

export default useRealtimePL;
