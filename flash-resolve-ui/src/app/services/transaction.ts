import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// This interface mirrors your Java Transaction model
export interface Transaction {
  id: string;
  userId: string;
  merchantId: string;
  amount: number;
  timestamp: string;
  location: string;
  status: string;
  riskScore: number;
  aiExplanation: string;
}

@Injectable({
  providedIn: 'root'
})
export class TransactionService {
  // Pointing directly to your local Java API
  private apiUrl = 'http://localhost:8081/api/transactions';

  constructor(private http: HttpClient) { }

  // Fetches the list of transactions from PostgreSQL via Java
  getAllTransactions(): Observable<Transaction[]> {
    return this.http.get<Transaction[]>(this.apiUrl);
  }
}