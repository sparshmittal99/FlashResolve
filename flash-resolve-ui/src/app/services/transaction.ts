import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

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
  private apiUrl = 'https://flashresolve.onrender.com/api/transactions';

  constructor(private http: HttpClient) { }

  getAllTransactions(): Observable<Transaction[]> {
    return this.http.get<Transaction[]>(this.apiUrl);
  }

  // 🟢 NEW: Method to send a new transaction to Java
  createTransaction(transactionData: any): Observable<Transaction> {
    return this.http.post<Transaction>(this.apiUrl, transactionData);
  }
}