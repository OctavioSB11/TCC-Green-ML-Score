"""
Callbacks Layer (Seção 4.1.4 do TCC)

Este módulo destina-se a abrigar integrações nativas com bibliotecas que
suportam arquitetura orientada a eventos (ex: Hugging Face Trainer, Keras,
PyTorch Lightning). As callbacks interceptam hooks (como `on_epoch_end`)
para interagir com o GreenMLTracker em tempo real.
"""
