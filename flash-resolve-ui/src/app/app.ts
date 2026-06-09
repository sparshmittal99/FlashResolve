import { Component, OnInit, OnDestroy, signal } from '@angular/core';
import { FormsModule } from '@angular/forms'; // 🟢 1. Added for two-way data binding [(ngModel)]
import { CommonModule } from '@angular/common'; 
import { TransactionService, Transaction } from './services/transaction';
import { interval, Subscription } from 'rxjs';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule], // 🟢 2. Added FormsModule to the imports list
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class AppComponent implements OnInit, OnDestroy {
  transactions = signal<Transaction[]>([]);
  private pollingSub?: Subscription;

  // 🟢 3. Data model initialized for your test transaction generator form
  newTxn = {
    userId: 'test-user-123',
    merchantId: '',
    amount: null,
    location: ''
  };

  constructor(private transactionService: TransactionService) {}

  ngOnInit() {
    this.fetchData();

    // Start the heartbeat! Fetch new data every 3 seconds
    this.pollingSub = interval(3000).subscribe(() => {
      this.fetchData();
    });
  }

  fetchData() {
    this.transactionService.getAllTransactions().subscribe({
      next: (data: Transaction[]) => {
        this.transactions.set(data);
      },
      error: (err: any) => {
        console.error('Failed to fetch from Java API', err);
      }
    });
  }

  // 🟢 4. Function called when clicking the submission button on your HTML form
  submitTransaction() {
    // Basic frontend validation to avoid empty network calls
    if (!this.newTxn.merchantId || !this.newTxn.amount || !this.newTxn.location) {
      alert('Please fill out all fields before sending!');
      return;
    }

    // Fire the POST request to your Java Gateway
    this.transactionService.createTransaction(this.newTxn).subscribe({
      next: (response) => {
        console.log('🚀 Transaction pushed successfully onto Redis Queue via Java API!', response);
        
        // Force an immediate fetch so you don't even have to wait 3 seconds for the heartbeat
        this.fetchData(); 

        // Clear the form fields back to empty defaults
        this.newTxn = {
          userId: 'test-user-123',
          merchantId: '',
          amount: null,
          location: ''
        };
      },
      error: (err: any) => {
        console.error('❌ Failed to route transaction through gateway:', err);
      }
    });
  }

  ngOnDestroy() {
    if (this.pollingSub) {
      this.pollingSub.unsubscribe();
    }
  }
}